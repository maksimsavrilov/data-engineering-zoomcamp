## Model deployment
[Tutorial](https://cloud.google.com/bigquery-ml/docs/export-model-tutorial)
### Steps
- gcloud auth login
- bq --project_id project-f2341c77-fecc-4b52-a12 extract -m zoomcamp_us.tip_model gs://tip_model/tip_model
- mkdir %TMP%/model
- gsutil cp -r gs://tip_model/tip_model %TMP%/model
- mkdir -p serving_dir/tip_model/1
- cp -r %TMP%/model/tip_model/* serving_dir/tip_model/1
- docker pull tensorflow/serving
- docker run -p 8501:8501 --mount type=bind,source=`pwd`/serving_dir/tip_model,target=/models/tip_model -e MODEL_NAME=tip_model -t tensorflow/serving &
- curl -d '{"instances": [{"passenger_count":1, "trip_distance":22.2, "pickup_location_id":"193", "dropoff_location_id":"264", "payment_type":"2","fare_amount":20.4,"tolls_amount":0.0}]}' -X POST http://localhost:8501/v1/models/tip_model:predict
- http://localhost:8501/v1/models/tip_model