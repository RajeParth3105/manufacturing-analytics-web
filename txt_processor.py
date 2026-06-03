import pandas as pd
from io import StringIO


def process_txt_files(uploaded_files):
    """
    Process multiple TXT files from EOL testing system.
    
    Args:
        uploaded_files: List of Streamlit UploadedFile objects
    
    Returns:
        Tuple of (master_df, summary_df, global_df)
    """
    
    all_data = []
    
    # Process each uploaded file
    for uploaded_file in uploaded_files:
        # Read file content
        content = uploaded_file.read().decode('utf-8', errors='replace')
        file_name = uploaded_file.name
        
        # Extract variant from filename (e.g., "report_VariantA.txt" -> "VariantA")
        variant = file_name.replace('.txt', '').replace('report_', '').replace('_', '')
        
        # Parse file content
        for line in content.split('\n'):
            if not line.strip():
                continue
                
            # Process only @PM lines
            if line.startswith('@PM'):
                parts = line.strip().split('\t')
                
                # Ensure enough columns exist
                if len(parts) >= 10:
                    pm_no = parts[0]
                    status = parts[1]
                    test_type = parts[4]
                    
                    # Convert comma decimals safely
                    value_str = parts[5].replace(',', '.')
                    min_limit_str = parts[7].replace(',', '.')
                    max_limit_str = parts[8].replace(',', '.')
                    
                    comment = parts[9] if len(parts) > 9 else ''
                    
                    all_data.append({
                        'File_Name': file_name,
                        'Variant': variant,
                        'PM_No': pm_no,
                        'Status': status,
                        'Test_Type': test_type,
                        'Value': value_str,
                        'Min_Limit': min_limit_str,
                        'Max_Limit': max_limit_str,
                        'Comment': comment,
                    })
    
    # Create master dataframe
    master_df = pd.DataFrame(all_data)
    
    # Convert numeric columns
    for col in ('Value', 'Min_Limit', 'Max_Limit'):
        master_df[col] = pd.to_numeric(master_df[col], errors='coerce')
    
    # Filter only NIO (Not In Order) records for summaries
    nio_df = master_df[master_df['Status'] == 'NIO']
    
    # Create failure summary (by Comment)
    if len(nio_df) > 0:
        failure_counts = (
            nio_df['Comment']
            .value_counts()
            .reset_index()
        )
        failure_counts.columns = ['Comment', 'NOK_Count']
        
        # Calculate percentage
        total_failures = failure_counts['NOK_Count'].sum()
        failure_counts['Failure_Percentage'] = (
            failure_counts['NOK_Count'] / total_failures * 100
        ).round(2)
        
        # Assign priority
        def assign_priority(percent):
            if percent >= 30:
                return 'HIGH'
            elif percent >= 10:
                return 'MEDIUM'
            else:
                return 'LOW'
        
        failure_counts['Priority'] = failure_counts['Failure_Percentage'].apply(assign_priority)
        
        summary_df = failure_counts.sort_values('Failure_Percentage', ascending=False)
    else:
        summary_df = pd.DataFrame(columns=['Comment', 'NOK_Count', 'Failure_Percentage', 'Priority'])
    
    # Create global failure summary (aggregate across all variants)
    if len(nio_df) > 0:
        global_counts = (
            nio_df['Comment']
            .value_counts()
            .reset_index()
        )
        global_counts.columns = ['Failure', 'Count']
        global_df = global_counts.sort_values('Count', ascending=False)
    else:
        global_df = pd.DataFrame(columns=['Failure', 'Count'])
    
    return master_df, summary_df, global_df
