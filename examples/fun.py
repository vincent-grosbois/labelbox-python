from typing import Union, List, Literal, Tuple
import numpy as np
from uuid import uuid4





class Mapper:
  def __init__(self, class_names):
    self.class_names = class_names

  def get_nested_annotation(self, nested_hierarchy, score):
    # Can confidence be provided in the nested classifications?
    if not len(nested_hierarchy):
      return {}

    if len(nested_hierarchy) % 2 != 0:
      raise ValueError("Must provide question and answer")

    root = parent = {}
    current = {}
    for i in range(0,len(nested_hierarchy), 2):
      current['name'] = nested_hierarchy[i]
      current['answer'] = {
        'name' : nested_hierarchy[i + 1],
        'confidence' : score
      }
      parent['classifications'] = current
      current = parent
    return root

  def get_bounding_box_annotation(self,
                              data_row_id: str,
                              bbox: Tuple[float, float, float, float],
                              index :int,
                              score: float):
    x1, y1, x2, y2 = bbox
    min_y, max_y = min(y1, y2), max(y1, y2)
    min_x, max_x = min(x1, x2), max(x1, x2)
    class_hierarchy = self.class_names[index].split(":")
    classifications = self.get_nested_annotation(class_hierarchy[1:], score)
    return {
        'uuid' : str(uuid4()),
        'name' : class_hierarchy[0],
        'bbox' : {
            'top' :    min_y,
            'left' :   min_x,
            'height' : max_y - min_y,
            'width' :  max_x - min_x
        },
        'dataRow' : {'id' : data_row_id},
        **({'confidence' : score} if score is not None else {}),
        **classifications
    }

  def get_classification_annotation(self,
              data_row_id: str,
              score: float,
              index :int):
    class_hierarchy = self.class_names[index].split(":")
    classifications = self.get_nested_annotation(class_hierarchy[2:], score)
    return {
        'name' : class_hierarchy[0],
        'uuid' : str(uuid4()),
        'dataRow' : {'id' : data_row_id},
        'answer' : {
            'name' : class_hierarchy[1]
        },
        **classifications
    }





def get_object_ndjson(mapper: Mapper, data_row_ids: List[str], bboxes: np.ndarray, scores: np.ndarray, background_index = 0):
  ...
  # First validate that predictions are in the valid format
  # bboxes -> [B,N,4] -> x1,y1,x2,y2 (as pixel detection)
  # scores -> [B,N,C] -> sum(C) == 1 (mutually exclusive classes)
  expected_n_classes = len(mapper.class_names)
  assert len(bboxes.shape) == 3
  assert len(scores.shape) == 3

  batch_size = len(data_row_ids)
  assert bboxes.shape[0] == scores.shape[0] == batch_size
  n_detections = bboxes.shape[1]
  assert n_detections == scores.shape[1]


  assert bboxes.shape[2] == 4
  assert scores.shape[2] == expected_n_classes

  ndjson = []
  argmax = np.argmax(scores, axis = -1)
  max_predicted_idx = np.max(argmax)
  if max_predicted_idx > (expected_n_classes- 1):
    raise ValueError(f"Predictions contain index {max_predicted_idx}. Expected only {expected_n_classes}")


  for batch_idx in range(batch_size):
    for detection_idx in range(n_detections):
      predicted_idx = argmax[detection_idx, batch_idx]

      if predicted_idx == 0:
        continue

      ndjson.append(
        mapper.get_bounding_box_annotation(
            data_row_ids[batch_idx],
            np.squeeze(bboxes[batch_idx, detection_idx,:]),
            predicted_idx,
            scores[batch_idx, detection_idx, argmax[detection_idx, batch_idx]],
        )
    )
  return ndjson


def get_classification_ndjson(mapper: Mapper, data_row_ids: List[str], scores: np.ndarray):
  # First validate that predictions are in the valid format
  # scores -> [B,C] -> mutually exclusive sum(C) == 1
  expected_n_classes = len(mapper.class_names)
  assert len(scores.shape) == 2
  assert scores.shape[0] == len(data_row_ids)
  assert scores.shape[1] == expected_n_classes

  ndjson = []
  argmax = np.argmax(scores, axis = -1)
  max_predicted_idx = np.max(argmax)
  if max_predicted_idx > (expected_n_classes- 1):
    raise ValueError(f"Predictions contain index {max_predicted_idx}. Expected only {expected_n_classes}")

  for idx, score in enumerate(scores):
    ndjson.append(
        mapper.get_classification_annotation(data_row_ids[idx], scores[idx, argmax[idx]], argmax[idx])
    )
  return ndjson





