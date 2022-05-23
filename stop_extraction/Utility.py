import pandas as pd

def read_traj_points_csv(path):
    df = pd.read_csv(path)
    id = df['id'].tolist()
    x = df['x'].tolist()
    y = df['y'].tolist()
    timestamp = df['timestamp'].tolist()
    return (df, [(id[i], i, (x[i],y[i]),timestamp[i]) for i in range(len(df))])

def write_output_csv(data, to_save_path):
    data.to_csv(to_save_path)