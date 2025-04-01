from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Sequence, Set
from typing import Type


def _rm_titles(kv: dict, prev_key: str = "") -> dict:
    new_kv = {}
    for k, v in kv.items():
        if k == "title":
            if isinstance(v, dict) and prev_key == "properties" and "title" in v.keys():
                new_kv[k] = _rm_titles(v, k)
            else:
                continue
        elif isinstance(v, dict):
            new_kv[k] = _rm_titles(v, k)
        else:
            new_kv[k] = v
    return new_kv


def _retrieve_ref(path: str, schema: dict) -> dict:
    components = path.split("/")
    if components[0] != "#":
        raise ValueError(
            "ref paths are expected to be URI fragments, meaning they should start "
            "with #."
        )
    out = schema
    for component in components[1:]:
        if component in out:
            out = out[component]
        elif component.isdigit() and int(component) in out:
            out = out[int(component)]
        else:
            raise KeyError(f"Reference '{path}' not found.")
    return deepcopy(out)


def _dereference_refs_helper(
        obj: Any,
        full_schema: Dict[str, Any],
        skip_keys: Sequence[str],
        processed_refs: Optional[Set[str]] = None,
) -> Any:
    if processed_refs is None:
        processed_refs = set()

    if isinstance(obj, dict):
        obj_out = {}
        for k, v in obj.items():
            if k in skip_keys:
                obj_out[k] = v
            elif k == "$ref":
                if v in processed_refs:
                    continue
                processed_refs.add(v)
                ref = _retrieve_ref(v, full_schema)
                full_ref = _dereference_refs_helper(
                    ref, full_schema, skip_keys, processed_refs
                )
                processed_refs.remove(v)
                return full_ref
            elif isinstance(v, (list, dict)):
                obj_out[k] = _dereference_refs_helper(
                    v, full_schema, skip_keys, processed_refs
                )
            else:
                obj_out[k] = v
        return obj_out
    elif isinstance(obj, list):
        return [
            _dereference_refs_helper(el, full_schema, skip_keys, processed_refs)
            for el in obj
        ]
    else:
        return obj


def _infer_skip_keys(
        obj: Any, full_schema: dict, processed_refs: Optional[Set[str]] = None
) -> List[str]:
    if processed_refs is None:
        processed_refs = set()

    keys = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "$ref":
                if v in processed_refs:
                    continue
                processed_refs.add(v)
                ref = _retrieve_ref(v, full_schema)
                keys.append(v.split("/")[1])
                keys += _infer_skip_keys(ref, full_schema, processed_refs)
            elif isinstance(v, (list, dict)):
                keys += _infer_skip_keys(v, full_schema, processed_refs)
    elif isinstance(obj, list):
        for el in obj:
            keys += _infer_skip_keys(el, full_schema, processed_refs)
    return keys


from pydantic import BaseModel


def dereference_refs(
        schema_obj: dict,
        *,
        full_schema: Optional[dict] = None,
        skip_keys: Optional[Sequence[str]] = None,
) -> dict:
    """Try to substitute $refs in JSON Schema.

    Args:
        schema_obj: The schema object to dereference.
        full_schema: The full schema object. Defaults to None.
        skip_keys: The keys to skip. Defaults to None.

    Returns:
        The dereferenced schema object.
    """

    full_schema = full_schema or schema_obj
    skip_keys = (
        skip_keys
        if skip_keys is not None
        else _infer_skip_keys(schema_obj, full_schema)
    )
    return _dereference_refs_helper(schema_obj, full_schema, skip_keys)


def convert_pydantic_to_openai_function(
        model: Type[BaseModel],
        *,
        name: Optional[str] = None,
        description: Optional[str] = None,
        rm_titles: bool = True,
):
    """Converts a Pydantic model to a function description for the OpenAI API.

    Args:
        model: The Pydantic model to convert.
        name: The name of the function. If not provided, the title of the schema will be
            used.
        description: The description of the function. If not provided, the description
            of the schema will be used.
        rm_titles: Whether to remove titles from the schema. Defaults to True.

    Returns:
        The function description.
    """
    if hasattr(model, "model_json_schema"):
        schema = model.model_json_schema()  # Pydantic 2
    else:
        schema = model.schema()  # Pydantic 1
    schema = dereference_refs(schema)
    schema.pop("definitions", None)
    title = schema.pop("title", "")
    default_description = schema.pop("description", "")
    return {
        "type": "function",
        "function": {
            "name": name or title,
            "description": description or default_description,
            "parameters": _rm_titles(schema) if rm_titles else schema,
        }
    }
