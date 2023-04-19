# coding=utf-8
# Copyright 2023 The HuggingFace Inc. team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" 
Conversion script for the T2I-Adapter checkpoints. 
Only models using the `Adapter-Light` architecture need this conversion,
the more common used `Adapter` architecture checkpoint can be use by diffuers `T2IAdapter` without conversion.
"""

import re
import argparse

import torch


def convert_adapter_light(old_state_dict):
    mapping = {
        "body.0.in_conv.bias": "conv_in.bias",
        "body.0.in_conv.weight": "conv_in.weight",
        "body.0.out_conv.bias": "body.3.out_conv.bias",
        "body.0.out_conv.weight": "body.3.out_conv.weight",
        "body.1.in_conv.bias": "body.4.in_conv.bias",
        "body.1.in_conv.weight": "body.4.in_conv.weight",
        "body.1.out_conv.bias": "body.7.out_conv.bias",
        "body.1.out_conv.weight": "body.7.out_conv.weight",
        "body.2.in_conv.bias": "body.8.in_conv.bias",
        "body.2.in_conv.weight": "body.8.in_conv.weight",
        "body.2.out_conv.bias": "body.11.out_conv.bias",
        "body.2.out_conv.weight": "body.11.out_conv.weight",
        "body.3.in_conv.bias": "body.12.in_conv.bias",
        "body.3.in_conv.weight": "body.12.in_conv.weight",
        "body.3.out_conv.bias": "body.15.out_conv.bias",
        "body.3.out_conv.weight": "body.15.out_conv.weight",
    }
    cvr_state = {}
    resblock = re.compile(r"body\.(\d+)\.body\.(\d+)\.(.+)")
    for k, v in old_state_dict.items():
        m = resblock.match(k)
        if m:
            new_group = int(m.group(1)) * 4 + int(m.group(2))
            cvr_state[f"body.{new_group}.{m.group(3)}"] = v
        else:
            cvr_state[mapping[k]] = v
    return cvr_state


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--checkpoint_path", default=None, type=str, required=True, help="Path to the checkpoint to convert."
    )
    parser.add_argument(
        "--output_path", default=None, type=str, required=True, help="Path to the store the result checkpoint."
    )
    
    args = parser.parse_args()
    src_state = torch.load(args.checkpoint_path)
    res_state = convert_adapter_light(src_state)
    torch.save(res_state, args.output_path)