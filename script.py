import json
from typing import Dict, List, Optional
from collections import defaultdict
from pydantic import BaseModel, Field

# Data class for token information
class Token(BaseModel):
    id: str
    text: str
    lemma: str
    pos: str
    pos_finegrained: str
    feats: str
    start_char: str
    end_char: str

# Pydantic model for lemma information
class LemmaInfo(BaseModel):
    lemma: str
    pos: str
    inflection_info: Optional[List[str]] = Field(default_factory=list)
    total_frequency: int = 0
    wordforms: Dict[str, int] = Field(default_factory=dict)

# Pydantic model for output containing lemma information
class OutputData(BaseModel):
    lemmas: List[LemmaInfo]

# Function to process input data from JSON file and calculate required information
def process_json_input(input_file):
    lemma_data = defaultdict(lambda: {"inflection_info": [], "total_frequency": 0, "wordforms": defaultdict(int)})
    
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    for sentence_data in data['sentences']:
        for token_data in sentence_data['tokens']:
            lemma = token_data['lemma']
            pos = token_data['pos']
            inflection = token_data['feats']
            wordform = token_data['text']
            
            lemma_data[lemma]['pos'] = pos
            if inflection:
                if inflection not in lemma_data[lemma]['inflection_info']:
                    lemma_data[lemma]['inflection_info'].append(inflection)
            
            lemma_data[lemma]['total_frequency'] += 1
            lemma_data[lemma]['wordforms'][wordform] += 1
    
    lemma_info_list = [LemmaInfo(lemma=key,
                                 pos=value['pos'],
                                 inflection_info=value['inflection_info'],
                                 total_frequency=value['total_frequency'],
                                 wordforms=dict(value['wordforms']))
                       for key, value in lemma_data.items()]
    
    return OutputData(lemmas=lemma_info_list)

# Main function
if __name__ == "__main__":
    input_file = "sample_parsed_sentences.json"
    output_data = process_json_input(input_file)
    
    # Save output to a JSON file
    output_file = "output.json"
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(output_data.dict(), f, indent=2)
