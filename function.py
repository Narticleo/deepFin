import os
import shutil
import numpy as np
import csv
import pandas as pd
import torch.nn.functional as F
import torch

database = 'database_test'
center_csv = database + '\\embeddind_center.csv'
embedding_size = 2048
fs = 'feature0'
fe = f'feature{embedding_size-1}'

def to_embedding(paths, recognizer):#######################################
    embds = recognizer.get_embeddings(paths)
    return embds

def find_center(embds):########################################
    return torch.mean(embds, dim=0).cpu().numpy()

#input : id_0123R, [path1, path2, path3......]
def combine_with_new_pics(id, new_paths, recognizer):

    #remove repeat picture
    origin_paths = [path for path in os.listdir(id)]
    for i in range(len(new_paths)-1, 0, -1):
        if os.path.basename(new_paths[i]) in origin_paths:
            new_paths = new_paths[:i] + new_paths[i+1:] 
            
    for path in new_paths:
        shutil.copyfile(path, os.path.join(id, os.path.basename(path)))

    new_embds = to_embedding(new_paths, recognizer)
    new_center = find_center(new_embds)
    new_num = len(new_paths)

    df = pd.read_csv(center_csv)
    id = os.path.basename(id)
    condition = df['id'] == id
    old_center = df.loc[condition, fs:fe].values
    old_num = df.loc[condition, 'pic_num'].iloc[0]

    total = new_num + old_num
    avg_center = new_center*(new_num/total) + old_center*(old_num/total)
    df.loc[condition, fs:fe] = avg_center
    df.loc[condition, 'pic_num'] = total
    df.to_csv(center_csv, index=False)
    return 'update done'

#input : 'database/id_0123R'
def recalculation_id(id_path, recognizer):
    if not os.path.exists(id_path):
        return 'choose folder!'
    if os.path.normpath(database) not in os.path.normpath(id_path):
        return 'failed! choose a database folder!'
    paths = [pic.path for pic in os.scandir(id_path) if pic.path.lower().endswith(('.jpg', '.png', '.jpeg'))]
    embds = to_embedding(paths, recognizer)
    center = find_center(embds)
    num = len(paths)
    id = os.path.basename(id_path)
    df = pd.read_csv(center_csv)
    condition = df['id'] == id
    df.loc[condition, fs:fe] = center
    df.loc[condition, 'pic_num'] = num
    df.to_csv(center_csv, index=False)
    return 'Recalculation done'

#input : 'query/id_0123R'
def create_new_id(id_path, new_id_name, recognizer):
    if not os.path.exists(id_path):
        return 'failed! choose folder!'
    if new_id_name.strip() == '':
        return 'failed! input new id name!'
    df = pd.read_csv(center_csv)
    condition = df['id'] == new_id_name
    if not df.loc[condition,].empty:
        return 'failed! repeated id'
    with open(center_csv, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([new_id_name])
    shutil.copytree(id_path, os.path.join(database, new_id_name))
    new_path = os.path.join(database, new_id_name)
    recalculation_id(new_path, recognizer)
    return 'success!'

def remove_id(id_path):
    if not os.path.exists(id_path):
        return 'failed! path not exists!'
    if os.path.normpath(database) not in os.path.normpath(id_path):
        return 'failed! choose a database folder!'
    id = os.path.basename(id_path)
    df = pd.read_csv(center_csv)
    df.drop(df[df['id'] == id].index, inplace=True)
    df.to_csv(center_csv, index=False)
    shutil.rmtree(id_path)
    return 'success!'

def initialize(recognizer):
    if os.path.exists(center_csv):
        os.remove(center_csv)

    with open(center_csv, 'w', newline='') as file:
        writer = csv.writer(file)
        header = ['id', 'pic_num']
        header += [f'feature{i}' for i in range(embedding_size)]
        writer.writerow(header)

    for id in os.scandir(database):
        if os.path.isfile(id.path):
            continue
        id_paths = [name.path for name in os.scandir(id.path)]
        if not id_paths:
            continue
        id_embds = to_embedding(id_paths, recognizer)
        id_num = len(id_paths)
        id_center = find_center(id_embds)
        id_name = os.path.basename(id.path)
        id_row = [id_name, id_num] + id_center.tolist()
        id_row = [str(info) for info in id_row]

        with open(center_csv, mode = 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(id_row)

def get_top10_folder(query_center):
    db_centers = []
    df = pd.read_csv(center_csv)
    for _, row in df.iterrows():
        id = row['id']
        gallery_center = row[fs:fe].values
        qc = torch.from_numpy(query_center.astype(np.float32))
        gc = torch.from_numpy(gallery_center.astype(np.float32))
        similarity = F.cosine_similarity(qc, gc, dim=0)
        db_centers.append((id, similarity.item()))

    db_centers.sort(key=lambda x:x[1], reverse=True)
    #id_0001R,id_0234L...............
    top10 = [os.path.join(database, db_centers[i][0]) for i in range(10)]
    top10threshold = [db_centers[i][1] for i in range(10)]
    return top10,top10threshold

def correct_path(path):
    if path[0] == '"' or path[0] == '\'':
        path = path[1:]
    if path[-1] == '"' or path[-1] == '\'':
        path = path[:-1]
    path = path.replace('\\', '/')
    return path