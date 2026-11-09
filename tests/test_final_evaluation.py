import json
import numpy as np
import pytest
from src.evaluation import nucle_final_evaluation as final
from src.training import nucle_final_selection as selection
from src.training.nucle_final_selection import save_encoder,load_encoder
from src.training.nucle_ablation import feature_indices
from src.features.nucle_features import TrainOnlyEncoder
from src.evaluation.metrics import scores

def test_pair_metric_keeps_predictions_outside_pair_as_false_negatives():
    c=np.zeros((5,5),dtype=int);c[3,3]=1;c[3,0]=1;c[4,4]=1;c[4,1]=1
    assert final.matrix_metric(c,[3,4])==pytest.approx(2/3)

def test_group_resampling_counts_entire_group_and_agrees_with_expansion():
    # Two errors from one essay group must move together, never sampled independently.
    cms=np.zeros((2,5,5),dtype=int);cms[0,0,0]=1;cms[0,1,0]=1;cms[1,2,2]=1
    weights=np.array([[2,0],[0,2],[1,1]])
    boot=(weights@cms.reshape(2,25)).reshape(-1,5,5)
    assert boot.sum((1,2)).tolist()==[4,2,3]
    expected=scores(['ArtOrDet','Prep']*2,['ArtOrDet','ArtOrDet']*2)['macro_f1']
    assert final.matrix_metric(boot)[0]==pytest.approx(expected)

def test_encoder_serialization_preserves_unknown_and_numeric_features(tmp_path):
    e=TrainOnlyEncoder().fit([{'sample_id':'train','partition':'train','features':{'S|length':2.,'P|pattern':'NOUN|VERB','L|span_ngrams':'cat'}}])
    p=tmp_path/'encoder.json';save_encoder(e,p);r=load_encoder(p)
    f={'S|length':5.,'P|pattern':'unseen','L|span_ngrams':'dog'}
    assert e.transform_one(f)==r.transform_one(f)
    assert r.train_ids=={'train'}

def test_explicit_family_removal_and_full_minus_d_alias():
    names=['N|S|size','C|P|pos|NOUN','C|M|Number|Sing','C|D|head_pos|VERB','L|span_ngrams|x']
    assert feature_indices(names,'Full_minus_P',set('SLMD'))==[0,2,3,4]
    assert feature_indices(names,'Full_minus_D',set('SLPM'))==feature_indices(names,'S+L+P+M',set('SLPM'))

def test_lock_rejects_changed_frozen_input(tmp_path,monkeypatch):
    monkeypatch.setattr(final,'ROOT',tmp_path);monkeypatch.setattr(final,'OUT',tmp_path)
    p=tmp_path/'input.txt';p.write_text('original')
    lock=tmp_path/'lock.json';lock.write_text(json.dumps({'hashes':{'input.txt':final.sha(p)}}))
    (tmp_path/'lock.sha256').write_text(final.sha(lock))
    final.verify_lock();p.write_text('changed')
    with pytest.raises(AssertionError):final.verify_lock()


def test_selection_reaches_data_loading_without_protocol(tmp_path, monkeypatch):
    monkeypatch.setattr(selection, 'ROOT', tmp_path)
    monkeypatch.setattr(selection, 'OUT', tmp_path / 'output')
    monkeypatch.setattr(selection.torch, 'set_num_threads', lambda count: None)
    class DataLoadingReached(Exception):
        pass

    def stop_at_data_loading(*args):
        raise DataLoadingReached

    monkeypatch.setattr(selection, 'load_rows', stop_at_data_loading)
    with pytest.raises(DataLoadingReached):
        selection.run()
    record = selection.read(selection.OUT / 'selection_started.json')
    assert 'protocol_sha256' not in record
    assert record['test_scored'] is False


@pytest.fixture
def freeze_workspace(tmp_path, monkeypatch):
    for name, path in {
        'ROOT': tmp_path,
        'OUT': tmp_path / 'reports/final_evaluation',
        'PREP': tmp_path / 'data_set/processed/nucle_preparation',
        'SPLIT': tmp_path / 'data_set/split/nucle_group_split',
        'FEAT': tmp_path / 'data_set/features/nucle_features',
    }.items():
        monkeypatch.setattr(selection, name, path)
    monkeypatch.setattr(final, 'ROOT', tmp_path)
    monkeypatch.setattr(final, 'OUT', selection.OUT)

    # Minimal completed-selection artifacts; freeze hashes bytes without loading models.
    files = {
        selection.PREP: ['samples.jsonl', 'manifest.json', 'manifest.sha256'],
        selection.SPLIT: ['split_manifest.csv', 'essay_groups.csv'],
        selection.FEAT: ['features.jsonl', 'targets.jsonl', 'encoder.json', 'manifest.json'],
        selection.OUT: ['full_encoder.json', 'masked_encoder.json', 'pos_rule.json',
                        'encoder_verification.json', 'validation_predictions.csv'],
        selection.OUT / 'checkpoints': ['LR_03.pt', 'Tree_03.pt'],
        tmp_path / 'src': ['example.py'],
        tmp_path: ['uv.lock', 'pyproject.toml'],
    }
    for directory, names in files.items():
        directory.mkdir(parents=True, exist_ok=True)
        for name in names:
            (directory / name).write_text('synthetic artifact', encoding='utf-8')
    selection.dump(selection.OUT / 'selection_summary.json', {
        'selected': [{'id': i} for i in range(18)], 'unique_fits': 52,
    })
    return tmp_path


def test_freeze_ignores_protocol_and_still_verifies_artifacts(freeze_workspace):
    protocol = freeze_workspace / 'docs/final_evaluation_protocol.md'
    protocol.parent.mkdir()
    protocol.write_text('Experiment plan', encoding='utf-8')

    selection.freeze()
    lock = final.verify_lock()
    protocol_key = str(protocol.relative_to(freeze_workspace))
    assert protocol_key not in lock['hashes']
    protocol.write_text('Changed plan', encoding='utf-8')
    final.verify_lock()
    protocol.unlink()
    final.verify_lock()

    for artifact in (selection.PREP / 'samples.jsonl', selection.OUT / 'checkpoints/LR_03.pt'):
        original = artifact.read_bytes()
        artifact.write_text('Changed artifact', encoding='utf-8')
        with pytest.raises(AssertionError):
            final.verify_lock()
        artifact.write_bytes(original)
    final.verify_lock()


def test_freeze_still_requires_data_artifacts(freeze_workspace):
    (selection.PREP / 'samples.jsonl').unlink()
    with pytest.raises(FileNotFoundError):
        selection.freeze()
    assert not (selection.OUT / 'lock.json').exists()
