# GPL License
# Copyright (C) 2023 , UESTC
# All Rights Reserved
#
# @Time    : 2023/10/1 20:29
# @Author  : Qi Cao
import argparse
import h5py
from Toolbox.model_RSP import FusionNet
from Toolbox.indexes import *
import scipy.io as sio

# ================== Pre-Define =================== #
parser = argparse.ArgumentParser()
parser.add_argument("--satellite", type=str, default='wv3/', help="Satellite type")
parser.add_argument("--name", type=int, required=True, help="Data ID (0-19)")
args = parser.parse_args()

satellite = args.satellite
name = args.name
ckpt = f'model_FUG/{satellite}{name}'

model = FusionNet()
weight = torch.load(ckpt)
model.load_state_dict(weight)


###################################################################
# ------------------- Main Test (Run second)----------------------------------
###################################################################


def test():
    print("Test...")

    file_path = 'dataset/' + satellite + 'train.h5'
    dataset = h5py.File(file_path, 'r')
    ms = np.array(dataset['ms'][name], dtype=np.float32) / 2047.0
    lms = np.array(dataset['lms'][name], dtype=np.float32) / 2047.0
    pan = np.array(dataset['pan'][name], dtype=np.float32) / 2047.0

    ms = torch.from_numpy(ms).float()
    lms = torch.from_numpy(lms).float()
    pan = torch.from_numpy(pan).float()

    ms = torch.unsqueeze(ms.float(), dim=0)
    lms = torch.unsqueeze(lms.float(), dim=0)
    pan = torch.unsqueeze(pan.float(), dim=0)

    res = model(lms, pan)
    out = res + lms
    sr = torch.squeeze(out * 2047).permute(1, 2, 0).cpu().detach().numpy()
    I_pan = torch.squeeze(pan * 2047).cpu().detach().numpy()
    I_ms = torch.squeeze(lms * 2047).permute(1, 2, 0).cpu().detach().numpy()
    I_ms_lr = torch.squeeze(ms * 2047).permute(1, 2, 0).cpu().detach().numpy()

    I_SR = torch.squeeze(out*2047).permute(1, 2, 0).cpu().detach().numpy()  # HxWxC
    I_MS_LR = torch.squeeze(ms*2047).permute(1, 2, 0).cpu().detach().numpy()  # HxWxC
    I_MS = torch.squeeze(lms*2047).permute(1, 2, 0).cpu().detach().numpy()  # HxWxC
    I_PAN = torch.squeeze(pan*2047).cpu().detach().numpy()  # HxWxC

    sio.savemat('result/' + satellite + str(name) + '.mat', {'I_SR': I_SR, 'I_MS_LR': I_MS_LR, 'I_MS': I_MS, 'I_PAN': I_PAN})

###################################################################
# ------------------- Main Function (Run first) -------------------
###################################################################


if __name__ == "__main__":
    test()
