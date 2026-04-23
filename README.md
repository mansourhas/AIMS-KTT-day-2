Note the experments.ipynb run on Colab cpu instence, the reason i used colab is to make the time and latency bounds reproducable with an ancore (my core I9 might underestimate the constrain)

Note on ONNX: While you mentioned saving as .onix, converting LightGBM models to ONNX requires installing onnxmltools and skl2onnx, which can cause dependency conflicts in a strict Colab environment. Instead, I have used LightGBM's highly optimized, native .txt saving format (and joblib for scikit-learn wrappers) which is the industry standard for lightweight deployments.


windows:
training:
python src\forecaster.py --train --data dataset\grid_history.csv
python src\forecaster.py --predict --data dataset\recent_24h.csv

linx 
training:
python src/forecaster.py --train --data dataset/grid_history.csv
python src/forecaster.py --predict --data dataset/recent_24h.csv


python -m http.server