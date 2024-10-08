from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
from transformers import BertTokenizer, EncoderDecoderModel, BertGenerationEncoder, BertGenerationDecoder, Seq2SeqTrainer, TrainingArguments
import numpy as np
from torch.nn.utils.rnn import pad_sequence
from evaluate import load
import transformers.data
import torch
import json
import os


eng = []
acts = []
locs = [] 
n_obs = []
paths = []

with open('../single_goal/6x6worlds/dev_set.json') as f:
    data = json.load(f)

    for data_point in data:
        eng.append(data_point['nl_description'])
        acts.append(data_point['agent_as_a_point'])



print(len(set(eng)))



out = []

scores = {}

seen = []
while(True):

    checkpoints = os.listdir('T5_base_single_goal_point/')

    todo = []

    for checkpoint in checkpoints:
        if(checkpoint not in seen):
            todo.append(checkpoint)
    if(len(todo) == 0):
        break

    for checkpoint in todo:
        seen.append(checkpoint)
        tokenizer = T5Tokenizer.from_pretrained("t5-base")
        model = T5ForConditionalGeneration.from_pretrained('T5_base_single_goal_point/' + checkpoint)
        exact_match = 0
        with open('out_T5_base_sg_point_6x6_dev_' + checkpoint + '.json', 'w') as fo:
            with torch.no_grad():
                for j in range(len(eng)): 
                    
                    example = eng[j]
                    sol = acts[j]

                    input_ids = tokenizer(example, return_tensors="pt").input_ids
                    generated_ids = model.generate(input_ids, max_length=512, decoder_start_token_id=tokenizer.bos_token_id)
                    generated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

                    print(generated_text, sol)
                    exact_match += (generated_text[0].replace(' ', '') == sol.replace(' ', '')) 

                    cat = {
                        'english': example,
                        'generated': generated_text,
                        'ground_truth': sol,
                    }
                            
                    out.append(cat)

                json_object = json.dumps(out, indent = 4)
                fo.write(json_object)
                fo.write('\n')
                print(exact_match / len(eng))
                scores[checkpoint] = exact_match / len(eng)

    with open('scores.json', 'w') as fo:
        json_object = json.dumps(scores, indent = 4)
        fo.write(json_object)
        fo.write('\n')

