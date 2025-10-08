from utils.file_util import read_json_file, write_json_to_file, iter_file_from_dir
import pandas as pd
import os
from metrics.qa_metrics import QAMetric


if __name__ == '__main__':
    # ==== Global settings ====
    PROJECT_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    experiment_name = '250731-fix'  # Change this to your experiment name

    # Input parsed results directory
    PARSED_RESULTS_DIR = f'{PROJECT_ROOT_DIR}/data/experiments/{experiment_name}/parsed_results'

    # Output evaluation results directory
    EVAL_RESULT_DIR = f'{PROJECT_ROOT_DIR}/data/experiments/{experiment_name}/evaluation_results'

    # Create output directory if it doesn't exist
    os.makedirs(EVAL_RESULT_DIR, exist_ok=True)

    qa_metric = QAMetric()

    # Get all parsed result files
    parsed_files = []
    for file_path in iter_file_from_dir(PARSED_RESULTS_DIR, '.jsonl'):
        data = read_json_file(file_path)
        input_type = data[0]['input_type']
        model_name = os.path.basename(file_path).split('=')[0]

        # Group data by layout_complexity_level
        complexity_groups = {}
        for sample in data:
            complexity_level = sample.get('layout_complexity_level', 'Unknown')
            if complexity_level not in complexity_groups:
                complexity_groups[complexity_level] = []
            complexity_groups[complexity_level].append(sample)

        # Group data by reasoning_level
        reasoning_groups = {}
        for sample in data:
            reasoning_level = sample.get('reasoning_level', 'Unknown')
            if reasoning_level not in reasoning_groups:
                reasoning_groups[reasoning_level] = []
            reasoning_groups[reasoning_level].append(sample)

        # Group data by combined reasoning and complexity level
        combined_groups = {}
        for sample in data:
            reasoning_level = sample.get('reasoning_level', 'Unknown')
            complexity_level = sample.get('layout_complexity_level', 'Unknown')
            combined_key = f"{reasoning_level}-{complexity_level}"
            if combined_key not in combined_groups:
                combined_groups[combined_key] = []
            combined_groups[combined_key].append(sample)

        # Evaluate each complexity level separately
        all_results = {}
        for complexity_level, samples in complexity_groups.items():
            predictions = [sample['parsed_result']
                           ['parsed_prediction'] for sample in samples]
            references = [sample['answer'] for sample in samples]

            result = qa_metric.compute(references, predictions)
            all_results[complexity_level] = result

            print(f"Model: {model_name}, Input Type: {input_type}, Layout Complexity: {complexity_level}, "
                  f"EM: {result['EM']}, EM_with_error_2: {result['EM_with_error_2']}, "
                  f"EM_with_error_5: {result['EM_with_error_5']}, EM_with_error_10: {result['EM_with_error_10']}")

        # Evaluate each reasoning level separately
        reasoning_results = {}
        for reasoning_level, samples in reasoning_groups.items():
            predictions = [sample['parsed_result']
                           ['parsed_prediction'] for sample in samples]
            references = [sample['answer'] for sample in samples]

            result = qa_metric.compute(references, predictions)
            reasoning_results[reasoning_level] = result

            print(f"Model: {model_name}, Input Type: {input_type}, Reasoning Level: {reasoning_level}, "
                  f"EM: {result['EM']}, EM_with_error_2: {result['EM_with_error_2']}, "
                  f"EM_with_error_5: {result['EM_with_error_5']}, EM_with_error_10: {result['EM_with_error_10']}")

        # Evaluate each combined level separately
        combined_results = {}
        for combined_key, samples in combined_groups.items():
            predictions = [sample['parsed_result']
                           ['parsed_prediction'] for sample in samples]
            references = [sample['answer'] for sample in samples]

            result = qa_metric.compute(references, predictions)
            combined_results[combined_key] = result

            print(f"Model: {model_name}, Input Type: {input_type}, Combined Level: {combined_key}, "
                  f"EM: {result['EM']}, EM_with_error_2: {result['EM_with_error_2']}, "
                  f"EM_with_error_5: {result['EM_with_error_5']}, EM_with_error_10: {result['EM_with_error_10']}")

        # Overall results (for comparison)
        all_predictions = [sample['parsed_result']
                           ['parsed_prediction'] for sample in data]
        all_references = [sample['answer'] for sample in data]
        overall_result = qa_metric.compute(all_references, all_predictions)

        print(f"Model: {model_name}, Input Type: {input_type}, Layout Complexity: Overall, "
              f"EM: {overall_result['EM']}, EM_with_error_2: {overall_result['EM_with_error_2']}, "
              f"EM_with_error_5: {overall_result['EM_with_error_5']}, EM_with_error_10: {overall_result['EM_with_error_10']}")
        print("=" * 80)

        # Save detailed results to JSON file
        json_output_file = f"{EVAL_RESULT_DIR}/{model_name}_{input_type}_complexity_evaluation.json"
        detailed_results = {
            'model_name': model_name,
            'input_type': input_type,
            'overall': overall_result,
            'by_complexity': all_results,
            'by_reasoning': reasoning_results,
            'by_combined': combined_results,
            'sample_counts': {
                'complexity': {level: len(samples) for level, samples in complexity_groups.items()},
                'reasoning': {level: len(samples) for level, samples in reasoning_groups.items()},
                'combined': {level: len(samples) for level, samples in combined_groups.items()}
            }
        }
        write_json_to_file(json_output_file, detailed_results)
        
        # Prepare data for CSV export
        csv_data = []
        
        # Add overall results
        csv_data.append({
            'model_name': model_name,
            'input_type': input_type,
            'layout_complexity': 'Overall',
            'sample_count': len(data),
            'EM': overall_result['EM'],
            'EM_with_error_2': overall_result['EM_with_error_2'],
            'EM_with_error_5': overall_result['EM_with_error_5'],
            'EM_with_error_10': overall_result['EM_with_error_10']
        })
        
        # Add results by complexity level
        for complexity_level, result in all_results.items():
            csv_data.append({
                'model_name': model_name,
                'input_type': input_type,
                'layout_complexity': complexity_level,
                'sample_count': len(complexity_groups[complexity_level]),
                'EM': result['EM'],
                'EM_with_error_2': result['EM_with_error_2'],
                'EM_with_error_5': result['EM_with_error_5'],
                'EM_with_error_10': result['EM_with_error_10']
            })
        
        # Save to CSV
        # csv_output_file = f"{EVAL_RESULT_DIR}/{model_name}_{input_type}_complexity_evaluation.csv"
        # df = pd.DataFrame(csv_data)
        # df.to_csv(csv_output_file, index=False, sep='\t')

        print(f"Results saved to:")
        print(f"  JSON: {json_output_file}")
        # print(f"  CSV: {csv_output_file}")
        
    # Create a summary CSV with all models and input types
    print("\nCreating summary CSV...")
    summary_data = []
    
    # Re-read all files to create comprehensive summary
    for file_path in iter_file_from_dir(PARSED_RESULTS_DIR, '.jsonl'):
        data = read_json_file(file_path)
        input_type = data[0]['input_type']
        model_name = os.path.basename(file_path).split('=')[0]
        
        # Group data by layout_complexity_level
        complexity_groups = {}
        for sample in data:
            complexity_level = sample.get('layout_complexity_level', 'Unknown')
            if complexity_level not in complexity_groups:
                complexity_groups[complexity_level] = []
            complexity_groups[complexity_level].append(sample)
        
        # Overall results
        all_predictions = [sample['parsed_result']['parsed_prediction'] for sample in data]
        all_references = [sample['answer'] for sample in data]
        overall_result = qa_metric.compute(all_references, all_predictions)
        
        summary_data.append({
            'model_name': model_name,
            'input_type': input_type,
            'layout_complexity': 'Overall',
            'sample_count': len(data),
            'EM': overall_result['EM'],
            'EM_with_error_2': overall_result['EM_with_error_2'],
            'EM_with_error_5': overall_result['EM_with_error_5'],
            'EM_with_error_10': overall_result['EM_with_error_10']
        })
        
        # Results by complexity level
        for complexity_level, samples in complexity_groups.items():
            predictions = [sample['parsed_result']['parsed_prediction'] for sample in samples]
            references = [sample['answer'] for sample in samples]
            result = qa_metric.compute(references, predictions)
            
            summary_data.append({
                'model_name': model_name,
                'input_type': input_type,
                'layout_complexity': complexity_level,
                'sample_count': len(samples),
                'EM': result['EM'],
                'EM_with_error_2': result['EM_with_error_2'],
                'EM_with_error_5': result['EM_with_error_5'],
                'EM_with_error_10': result['EM_with_error_10']
            })
    
    # Save summary CSV for each EM metric
    summary_df = pd.DataFrame(summary_data)
    # Sort by model, input_type, and complexity level for better readability
    summary_df = summary_df.sort_values(['model_name', 'input_type', 'layout_complexity'])
    
    # Generate separate CSV files for each EM metric
    em_metrics = ['EM', 'EM_with_error_2', 'EM_with_error_5', 'EM_with_error_10']
    
    for metric in em_metrics:
        # Create a CSV with only the specific metric
        metric_df = summary_df[['model_name', 'input_type', 'layout_complexity', 'sample_count', metric]].copy()
        metric_csv_file = f"{EVAL_RESULT_DIR}/all_models_complexity_evaluation_summary_{metric}.csv"
        metric_df.to_csv(metric_csv_file, index=False, sep='\t')
        print(f"Summary CSV for {metric} saved to: {metric_csv_file}")
    
    # Also save the complete summary CSV
    summary_csv_file = f"{EVAL_RESULT_DIR}/all_models_complexity_evaluation_summary_complete.csv"
    summary_df.to_csv(summary_csv_file, index=False, sep='\t')
    print(f"Complete summary CSV saved to: {summary_csv_file}")
    
    # Create a summary CSV with all models by reasoning level
    print("\nCreating reasoning level summary CSV...")
    reasoning_summary_data = []
    
    # Re-read all files to create comprehensive summary by reasoning level
    for file_path in iter_file_from_dir(PARSED_RESULTS_DIR, '.jsonl'):
        data = read_json_file(file_path)
        input_type = data[0]['input_type']
        model_name = os.path.basename(file_path).split('=')[0]
        
        # Group data by reasoning_level
        reasoning_groups = {}
        for sample in data:
            reasoning_level = sample.get('reasoning_level', 'Unknown')
            if reasoning_level not in reasoning_groups:
                reasoning_groups[reasoning_level] = []
            reasoning_groups[reasoning_level].append(sample)
        
        # Overall results
        all_predictions = [sample['parsed_result']['parsed_prediction'] for sample in data]
        all_references = [sample['answer'] for sample in data]
        overall_result = qa_metric.compute(all_references, all_predictions)
        
        reasoning_summary_data.append({
            'model_name': model_name,
            'input_type': input_type,
            'reasoning_level': 'Overall',
            'sample_count': len(data),
            'EM': overall_result['EM'],
            'EM_with_error_2': overall_result['EM_with_error_2'],
            'EM_with_error_5': overall_result['EM_with_error_5'],
            'EM_with_error_10': overall_result['EM_with_error_10']
        })
        
        # Results by reasoning level
        for reasoning_level, samples in reasoning_groups.items():
            predictions = [sample['parsed_result']['parsed_prediction'] for sample in samples]
            references = [sample['answer'] for sample in samples]
            result = qa_metric.compute(references, predictions)
            
            reasoning_summary_data.append({
                'model_name': model_name,
                'input_type': input_type,
                'reasoning_level': reasoning_level,
                'sample_count': len(samples),
                'EM': result['EM'],
                'EM_with_error_2': result['EM_with_error_2'],
                'EM_with_error_5': result['EM_with_error_5'],
                'EM_with_error_10': result['EM_with_error_10']
            })
    
    # Save reasoning level summary CSV for each EM metric
    reasoning_summary_df = pd.DataFrame(reasoning_summary_data)
    # Sort by model, input_type, and reasoning level for better readability
    reasoning_summary_df = reasoning_summary_df.sort_values(['model_name', 'input_type', 'reasoning_level'])
    
    # Generate separate CSV files for each EM metric
    em_metrics = ['EM', 'EM_with_error_2', 'EM_with_error_5', 'EM_with_error_10']
    
    for metric in em_metrics:
        # Create a CSV with only the specific metric
        metric_df = reasoning_summary_df[['model_name', 'input_type', 'reasoning_level', 'sample_count', metric]].copy()
        metric_csv_file = f"{EVAL_RESULT_DIR}/all_models_reasoning_evaluation_summary_{metric}.csv"
        metric_df.to_csv(metric_csv_file, index=False, sep='\t')
        print(f"Reasoning level summary CSV for {metric} saved to: {metric_csv_file}")
    
    # Also save the complete reasoning level summary CSV
    reasoning_summary_csv_file = f"{EVAL_RESULT_DIR}/all_models_reasoning_evaluation_summary_complete.csv"
    reasoning_summary_df.to_csv(reasoning_summary_csv_file, index=False, sep='\t')
    print(f"Complete reasoning level summary CSV saved to: {reasoning_summary_csv_file}")
    print("\nEvaluation completed successfully!")
