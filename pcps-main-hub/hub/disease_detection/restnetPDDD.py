import os
import json
import torch.nn as nn
import torch
from PIL import Image
from torchvision import transforms

def disease_detection(image_path):
    list_diseases = [
        ("Bacterial Spot","use pesticide","tomato_bacterial_spot"),
        ("Early Blight", "use copper fungicide","tomato_early_blight"),
        ("Late Blight", "use chlorothalonil fungicide","tomato_late_blight"),
        ("Leaf Mold","increase ventilation","tomato_leaf_mold"),
        ("Septoria","mulch","tomato_septoria_leaf_spot"),
        ("Spider mites","apply insecticidal soap","tomato_spider_mites"),
        ("Target Spot","use mancozeb fungicide","tomato_target_spot"),
        ("Yellow leaf curl virus", "use sulfur-based fungicide","tomato_yellow_leaf_curl_virus"),
        ("Mosaic Virus","do not put in the compost pile","tomato_mosaic_virus"),
        ("Healthy","very healthy plant","tomato_healthy"),
    ]
    result = resnetAnal101(image_path)
    for disease in list_diseases:
        if result[0][1] == disease[2]:
            return [disease[0], result[0][2], disease[1]]
    return ["Prediction not conclusive", result[0][2], "Probably healthy"]
    # Prediction, probabilty, advice
    
    
def resnetAnal101(image_path):
    # loads device
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    # output
    output_list = []

    # Define data transformation for image preprocessing
    data_transform = transforms.Compose(
        [transforms.Resize(256),
         transforms.CenterCrop(224),
         transforms.ToTensor(),
         transforms.Normalize([0.416, 0.468, 0.355], [0.210, 0.206, 0.213])])
    
    # Read class_indict from JSON file
    json_path = 'disease_detection/class_indicesPDDD.json'
    assert os.path.exists(os.path.abspath(json_path)), f"file: '{os.path.abspath(json_path)}' does not exist."
    with open(os.path.abspath(json_path), "r") as json_file:
        class_indict = json.load(json_file)
    
    # Create an instance of the ResNet model
    model = resnet101(num_classes=120).to(device)
    
    # Load model weights
    weights_path = 'disease_detection/model/ResNet_101-ImageNet-model-99.pth'
    assert os.path.exists(os.path.abspath(weights_path)), f"file: '{os.path.abspath(weights_path)}' does not exist, please download the model here: http://pd.dd.samlab.cn/m/Pre-training-model/ResNet/ResNet_101-ImageNet-model-99.pth and then put it in the folder: './disease_detection/model/'"
    
    try:
        model.load_state_dict(torch.load(weights_path, map_location=device))
        print("Model weights loaded successfully.")
    except FileNotFoundError:
        print(f"Error: weights file not found at {weights_path}")
    except RuntimeError as e:
        print(f"Error loading model weights: {e}")
    
    # Perform prediction
    model.eval()
    with torch.no_grad():
        img = Image.open(image_path)
        img = data_transform(img)
        img = img.unsqueeze(0)  # Add batch dimension
        output = model(img.to(device)).cpu()
        predict = torch.softmax(output, dim=1)
        probs, classes = torch.max(predict, dim=1)
        pro = probs[0]
        cla = classes[0]
        print("image: {}  class: {}  prob: {:.3}".format(image_path,
                                                         class_indict[str(cla.numpy())],
                                                         pro.numpy()))
        # Output array
        class_name = class_indict[str(cla.numpy())]
        probability = pro.numpy()
        output_list.append([image_path, class_name, probability])
    
    return output_list

#credit paper: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10194370/

def resnet101(num_classes=1000, include_top=True):
    return ResNet(Bottleneck, [3, 4, 23, 3], num_classes=num_classes, include_top=include_top)

class Bottleneck(nn.Module):
    expansion = 4

    def __init__(self, in_channel, out_channel, stride=1, downsample=None,
                 groups=1, width_per_group=64):
        super(Bottleneck, self).__init__()

        width = int(out_channel * (width_per_group / 64.)) * groups

        self.conv1 = nn.Conv2d(in_channels=in_channel, out_channels=width,
                               kernel_size=1, stride=1, bias=False)  # squeeze channels
        self.bn1 = nn.BatchNorm2d(width)
        # -----------------------------------------
        self.conv2 = nn.Conv2d(in_channels=width, out_channels=width, groups=groups,
                               kernel_size=3, stride=stride, bias=False, padding=1)
        self.bn2 = nn.BatchNorm2d(width)
        # -----------------------------------------
        self.conv3 = nn.Conv2d(in_channels=width, out_channels=out_channel*self.expansion,
                               kernel_size=1, stride=1, bias=False)  # unsqueeze channels
        self.bn3 = nn.BatchNorm2d(out_channel*self.expansion)
        self.relu = nn.ReLU(inplace=True)
        self.downsample = downsample

    def forward(self, x):
        identity = x
        if self.downsample is not None:
            identity = self.downsample(x)

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        out += identity
        out = self.relu(out)

        return out

class ResNet(nn.Module):

    def __init__(self,
                 block,
                 blocks_num,
                 num_classes=1000,
                 include_top=True,
                 groups=1,
                 width_per_group=64):
        super(ResNet, self).__init__()
        self.include_top = include_top
        self.in_channel = 64

        self.groups = groups
        self.width_per_group = width_per_group

        self.conv1 = nn.Conv2d(3, self.in_channel, kernel_size=7, stride=2,
                               padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(self.in_channel)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        self.layer1 = self._make_layer(block, 64, blocks_num[0])
        self.layer2 = self._make_layer(block, 128, blocks_num[1], stride=2)
        self.layer3 = self._make_layer(block, 256, blocks_num[2], stride=2)
        self.layer4 = self._make_layer(block, 512, blocks_num[3], stride=2)
        if self.include_top:
            self.avgpool = nn.AdaptiveAvgPool2d((1, 1))  # output size = (1, 1)
            self.fc = nn.Linear(512 * block.expansion, num_classes)

        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')

    def _make_layer(self, block, channel, block_num, stride=1):
        downsample = None
        if stride != 1 or self.in_channel != channel * block.expansion:
            downsample = nn.Sequential(
                nn.Conv2d(self.in_channel, channel * block.expansion, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(channel * block.expansion))

        layers = []
        layers.append(block(self.in_channel,
                            channel,
                            downsample=downsample,
                            stride=stride,
                            groups=self.groups,
                            width_per_group=self.width_per_group))
        self.in_channel = channel * block.expansion

        for _ in range(1, block_num):
            layers.append(block(self.in_channel,
                                channel,
                                groups=self.groups,
                                width_per_group=self.width_per_group))

        return nn.Sequential(*layers)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        if self.include_top:
            x = self.avgpool(x)
            x = torch.flatten(x, 1)
            x = self.fc(x)

        return x
    
class BasicBlock(nn.Module):
    expansion = 1

    def __init__(self, in_channel, out_channel, stride=1, downsample=None, **kwargs):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=in_channel, out_channels=out_channel,
                               kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channel)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv2d(in_channels=out_channel, out_channels=out_channel,
                               kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channel)
        self.downsample = downsample

    def forward(self, x):
        identity = x
        if self.downsample is not None:
            identity = self.downsample(x)

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)

        out += identity
        out = self.relu(out)

        return out
