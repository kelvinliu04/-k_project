
import tensorflow as tf
import cv2
import numpy as np


def load_graph(frozen_graph_filename):
  with tf.gfile.GFile(frozen_graph_filename, 'rb') as file:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(file.read())
  with tf.Graph().as_default() as graph:
    tf.import_graph_def(graph_def)
  return graph


def draw(image, output, classname, conf_threshold=0.5, bbox_color=(50, 255, 50)):
  num_detections = output[0][0]
  detection_boxes = output[1][0]
  detection_scores = output[2][0]
  detection_classes = output[3][0]

  height, width = image.shape[:2]
  for i in range(0, int(num_detections)):
    if detection_scores[i] > conf_threshold:
      class_id = int(detection_classes[i])
      ymin = int(detection_boxes[i][0] * height)
      xmin = int(detection_boxes[i][1] * width)
      ymax = int(detection_boxes[i][2] * height)
      xmax = int(detection_boxes[i][3] * width)
      label = "{0}: {1:.2f}".format(classname[class_id], detection_scores[i])

      cv2.rectangle(image, (xmin, ymin), (xmax, ymax), bbox_color, 2)
      label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
      cv2.rectangle(image, (xmin, ymin-label_size[0][1]), (xmin+label_size[0][0], ymin+label_size[1]),
                    (255, 255, 255), cv2.FILLED)
      cv2.putText(image, label, (xmin, ymin), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)


def main():
  model_path = 'frozen_inference_graph.pb'
  #image_path = 'LPR/coco/train/2.jpg'
  image_path = '333.jpg'
  flag_out = True
  classname = ['-','car', 'motorbike']
  graph = load_graph(model_path)

  image = cv2.imread(image_path)
  img = cv2.resize(image, (512, 512))
  img = np.float32(img)

  t_input = graph.get_tensor_by_name("import/image_tensor:0")
  t_output = [
    graph.get_tensor_by_name("import/num_detections:0"),
    graph.get_tensor_by_name("import/detection_boxes:0"),
    graph.get_tensor_by_name("import/detection_scores:0"),
    graph.get_tensor_by_name("import/detection_classes:0")
  ]
  with tf.Session(graph=graph) as sess:
    output = sess.run(t_output, feed_dict={t_input: [img]})

  draw(image, output, classname)

  if flag_out:
    cv2.imwrite("out.jpg", image)
  else:
    cv2.imshow('Image', image)
    cv2.waitKey(0)


if __name__ == "__main__":
  main()