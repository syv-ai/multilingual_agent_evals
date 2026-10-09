r"""EuroEval registrations for the public MultiBFCL languages missing in v18.3.

EuroEval loads DatasetConfig instances from this file automatically when run
from the repository root. Select a dataset explicitly, for example:

    uv run --no-project --python 3.12 --with euroeval==18.3.0 \
        euroeval --dataset multi-bfcl-ab --model dummy \
        --evaluate-test-split --num-iterations 1 --no-save-results

Do not run EuroEval without --dataset: that may benchmark every compatible
dataset. The source inventory is the 305 test-only configurations of
syvai/multi-bfcl at revision 5c29d74c60f61849a687b0e51586587b53788b3c.
This file adds the 273 configurations absent from EuroEval v18.3.0; its 31
translated MultiBFCL registrations include Portuguese (source code pt-pt),
and English is already available as BFCL-v2. The local registrations read the
public source directly; built-in EuroEval configurations may use derived minis.
Recheck this list when either EuroEval or the public dataset changes.
"""

import json

from datasets import Dataset, DatasetDict
from euroeval import DatasetConfig
from euroeval.languages import get_language
from euroeval.tasks import TOOL_CALLING

SOURCE = "syvai/multi-bfcl"

# Hub card configuration inventory minus EuroEval's 31 translated languages and
# English. European Portuguese (pt-pt) is registered by EuroEval as pt.
MISSING_LANGUAGE_CODES: tuple[str, ...] = tuple(
    """ab ace ady af alt am ami an ang anp ar arc ary arz as ast atj av avk awa ay az
    azb ba ban bar bcl bi bjn blk bm bn bo bpy br bug bxr cdo ce ceb ch chr chy
    ckb co cr crh csb cu cv cy dag din diq dsb dty dv dz ee eo eu ext fa fat ff fj
    fon frp frr fur fy ga gag gan gcr gd gl glk gn gom gor got gpe gu guc gur guw
    gv ha hak haw he hi hif hsb ht hy hyw ia id ie ig ik ilo inh io iu ja jam jbo
    ka kaa kab kbd kbp kcg kg ki kk kl km kn ko koi krc ks ku kv kw ky la lad lbe
    lez lfn lg li lij lld lmo ln lo ltg mad mai mdf mg mhr mi min mk ml mn mni mnw
    mr mrj ms mt mwl my myv mzn nap nds ne new nia nn nov nqo nso nv ny oc olo om
    or os pa pag pam pap pcd pcm pdc pfl pi pms pnb pnt ps pt-br pwn qu rm rmy rn
    ru rue rw sa sah sat sc scn sco sd se sg shi shn si skr sm smn sn so srn ss st
    stq su sw szl szy ta tay tcy te tet tg th ti tk tl tly tn to tpi tr trv ts tt
    tum tw ty tyv udm ug ur uz ve vec vep vi vls vo wa war wo wuu xal xh xmf yi yo
    yue za zea zh-cn zh-tw zu""".split()
)


def _preprocess(dataset: DatasetDict) -> DatasetDict:
    """Convert public BFCL records into EuroEval's tool-calling format.

    Args:
        dataset:
            Source dataset with its test split.

    Returns:
        A dataset containing text, function schemas, references and source IDs.
    """
    test = dataset["test"]
    assert isinstance(test, Dataset)
    converted = test.map(
        _convert_row,
        remove_columns=[column for column in test.column_names if column != "id"],
    )
    assert isinstance(converted, Dataset)
    return DatasetDict({"test": converted})


def _convert_row(row: dict[str, str]) -> dict[str, str]:
    """Format a MultiBFCL question and answer for EuroEval's task.

    Args:
        row:
            Row with JSON-encoded question, function and ground truth.

    Returns:
        The prompt, original function schema and possible answer calls.
    """
    messages = json.loads(row["question"])[0]
    if len(messages) == 1 and messages[0]["role"] == "user":
        question = f"Question: {messages[0]['content']}"
    else:
        role_labels = {"system": "System", "user": "Question", "assistant": "Assistant"}
        question = "\n".join(
            f"{role_labels.get(message['role'], message['role'].title())}: "
            f"{message['content']}"
            for message in messages
        )
    functions = json.dumps(json.loads(row["function"]), ensure_ascii=False)
    answers = json.dumps(json.loads(row["ground_truth"]), ensure_ascii=False)
    return {
        "text": f"Functions:\n{functions}\n{question}",
        "function": functions,
        "target_text": answers,
    }


# EuroEval's custom-dataset loader discovers module-level DatasetConfig values,
# not entries inside a list or dictionary. Keep the inventory static so loading
# the config file does not make 273 Hub API requests.
for _code in MISSING_LANGUAGE_CODES:
    _language = get_language(_code)
    if _language is None:
        raise ValueError(f"EuroEval does not support MultiBFCL language {_code!r}")
    globals()[f"MULTI_BFCL_{_code.upper().replace('-', '_')}_CONFIG"] = DatasetConfig(
        name=f"multi-bfcl-{_code}",
        pretty_name=f"MultiBFCL-{_code}",
        source=f"{SOURCE}::{_code}",
        task=TOOL_CALLING,
        languages=[_language],
        train_split=None,
        val_split=None,
        test_split="test",
        preprocessing_func=_preprocess,
        bootstrap_samples=True,
        unofficial=True,
    )
