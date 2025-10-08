import re
import os
from utils.file_util import read_json_file, write_json_to_file, iter_file_from_dir

# ==== Prediction Parsers ===


# def parse_dp_prediction(prediction):
#     pattern = r"Final Answer: (.+)"
#     try:
#         match = re.search(pattern, prediction)
#         if match:
#             return match.group(1)
#         else:
#             return ''
#     except Exception as e:
#         return ''

def parse_dp_prediction(prediction: str, model_name: str) -> str:
    """Extract the last 'Final Answer: ...' value from the prediction text."""
    prediction = prediction.strip()
    if 'table-llava' in model_name.lower():
        # 提取最后一个数字（支持整数和小数）
        match = re.findall(r'-?\d+(?:\.\d+)?', prediction)
        if match:
            parsed_prediction = match[-1]  # 取最后一个匹配到的数字
        else:
            parsed_prediction = ''
    else:
        # 对其他模型的预测结果进行通用处理
        matches = re.findall(r"Final Answer:\s*([-\d.,\s]+)", prediction)
        parsed_prediction = matches[-1].strip() if matches else ''
    return parsed_prediction


def preprocess_prediction_by_model(prediction: str, model_name: str) -> str:
    """Model-specific prediction preprocessing"""
    # Llama-VL 模型专门处理：取出ASSISTANT的回答
    if 'llama' in model_name.lower() or 'Llama' in model_name:
        if 'ASSISTANT' in prediction:
            prediction = prediction.split('ASSISTANT:')[-1].strip()

    # 可以在这里添加其他模型的专门处理逻辑
    # if 'qwen' in model_name.lower():
    #     # Qwen模型的专门处理
    #     pass
    # if 'internvl' in model_name.lower():
    #     # InternVL模型的专门处理
    #     pass

    return prediction


def parse_inference_results(inference_results):
    # === Start parsing ===
    parsed_results = []
    for sample in inference_results:
        prediction = sample['prediction']

        # 获取模型名称（从文件名或sample中提取）
        model_name = sample.get('model_name', '')

        # 模型专门的预处理
        prediction = preprocess_prediction_by_model(prediction, model_name)

        # For all instruction types, use direct prediction parsing
        parsed_prediction = parse_dp_prediction(prediction, model_name)

        parsed_result = {'parsed_prediction': parsed_prediction}

        # Process successful parsing ratio
        if parsed_prediction == '':
            parsed_result['Parse@1'] = False
        else:
            parsed_result['Parse@1'] = True

        # Save parsed result
        sample['parsed_result'] = parsed_result
        parsed_results.append(sample)
    return parsed_results


if __name__ == '__main__':
    # ==== Global settings ====
    PROJECT_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    EXP_DIR = 'data/experiments/250731-fix'

    INFERENCE_RESULT_DIR = f'{PROJECT_ROOT_DIR}/{EXP_DIR}/inference_results'
    PARSED_RUSULT_DIR = f'{PROJECT_ROOT_DIR}/{EXP_DIR}/parsed_results'

    # ==== Load inference results ====
    for inference_result_file in iter_file_from_dir(f'{INFERENCE_RESULT_DIR}', '.jsonl'):
        print(f'Parsing {inference_result_file}')

        # 从文件名中提取模型名称
        model_name = os.path.basename(inference_result_file).split('=')[0]

        # === Load inference results ===
        inference_results = read_json_file(inference_result_file)
        if not isinstance(inference_results, list):
            inference_results = [inference_results]

        # 为每个sample添加模型名称信息
        for sample in inference_results:
            sample['model_name'] = model_name

        # === Parse inference results ===
        parsed_results = parse_inference_results(inference_results)
        # === Save parsed results ===
        write_json_to_file(
            f'{PARSED_RUSULT_DIR}/{os.path.basename(inference_result_file)}', parsed_results, is_json_line=True)
    print('Parsing completed.')
