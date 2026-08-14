## Running Spark in the Cloud


### Enable access to internal google resources 
```
gcloud compute networks subnets update default \
--region=REGION_NAME \
--enable-private-ip-google-access
```

### Role reguired for VM service account to process tasks in Claster
```
gcloud projects get-iam-policy PROJECT_NAME \
--flatten="bindings[].members" \
--format='table(bindings.role)' \
--filter="bindings.members:767007221215-compute@developer.gserviceaccount.com"
```

```
# ROLE
# roles/dataproc.worker
```

### Role required to Dataproc service account
```
gcloud projects get-iam-policy PROJECT_NAME \
--flatten="bindings[].members" \
--filter="bindings.members:service-767007221215@dataproc-accounts.iam.gserviceaccount.com" \
--format="table(bindings.role)"
```

```
# ROLE
# roles/dataproc.serviceAgent
```

### Services to be enabled
```
gcloud services list \
--enabled \
--project=PROJECT_NAME \
--filter="name:cloudresourcemanager.googleapis.com"
```

```
# NAME                                 TITLE
# cloudresourcemanager.googleapis.com  Cloud Resource Manager API
```

### if not - enable
```
gcloud services enable cloudresourcemanager.googleapis.com   --project=PROJECT_NAME
```

### Just in case check service account is binded to you
```
gcloud iam service-accounts get-iam-policy \
767007221215-compute@developer.gserviceaccount.com \
--project=PROJECT_NAME
```

```
# bindings:
# - members:
#   - user:Maxim.Savrilov@gmail.com
#   role: roles/iam.serviceAccountUser
# etag: BwZY-93Q9Zo=
# version: 1
```

```
gcloud iam service-accounts add-iam-policy-binding \
767007221215-compute@developer.gserviceaccount.com \
--member="user:maxim.savrilov@gmail.com" \
--role="roles/iam.serviceAccountUser" \
--project=PROJECT_NAME
```

# Then create your cluster, the single node as example (optional component DOCKER fails to install for now)
```
gcloud dataproc clusters create cluster-working \
--enable-component-gateway \
--region=europe-west4 \
--subnet=default \
--no-address \
--single-node \
--master-machine-type=e2-standard-4 \
--master-boot-disk-type=pd-balanced \
--master-boot-disk-size=100 \
--image-version=2.3-debian12 \
--optional-components=ICEBERG,DELTA,JUPYTER \
--scopes='https://www.googleapis.com/auth/cloud-platform' \
--project=PROJECT_NAME \
--async
```

# For Docker it is required to create NAT router
```
gcloud compute routers create dataproc-router \
  --network=default \
  --region=europe-west4 \
  --project=PROJECT_NAME
gcloud compute routers nats create dataproc-nat \
  --router=dataproc-router \
  --region=europe-west4 \
  --nat-all-subnet-ip-ranges \
  --auto-allocate-nat-external-ips \
  --project=PROJECT_NAME
  ```

**Then use "cloud dataproc jobs submit pyspark" to send jobs to your claster**


### Connecting to Google Cloud Storage 

Uploading data to GCS:

```bash
gsutil -m cp -r pq/ gs://dtc_data_lake_de-zoomcamp-nytaxi/pq
```

Download the jar for connecting to GCS to any location (e.g. the `lib` folder):

**Note**: For other versions of GCS connector for Hadoop see [Cloud Storage connector ](https://cloud.google.com/dataproc/docs/concepts/connectors/cloud-storage#connector-setup-on-non-dataproc-clusters).

```bash
gsutil cp gs://hadoop-lib/gcs/gcs-connector-hadoop3-2.2.5.jar ./lib/
```

See the notebook with configuration in [09_spark_gcs.ipynb](09_spark_gcs.ipynb)

(Thanks Alvin Do for the instructions!)


### Local Cluster and Spark-Submit

Creating a stand-alone cluster ([docs](https://spark.apache.org/docs/latest/spark-standalone.html)):

```bash
./sbin/start-master.sh
```

Creating a worker:

```bash
URL="spark://de-zoomcamp.europe-west1-b.c.de-zoomcamp-nytaxi.internal:7077"
./sbin/start-slave.sh ${URL}

# for newer versions of spark use that:
#./sbin/start-worker.sh ${URL}
```

Turn the notebook into a script:

```bash
jupyter nbconvert --to=script 06_spark_sql.ipynb
```

Edit the script and then run it:

```bash 
python 06_spark_sql.py \
    --input_green=data/pq/green/2020/*/ \
    --input_yellow=data/pq/yellow/2020/*/ \
    --output=data/report-2020
```

Use `spark-submit` for running the script on the cluster

```bash
URL="spark://de-zoomcamp.europe-west1-b.c.de-zoomcamp-nytaxi.internal:7077"

spark-submit \
    --master="${URL}" \
    06_spark_sql.py \
        --input_green=data/pq/green/2021/*/ \
        --input_yellow=data/pq/yellow/2021/*/ \
        --output=data/report-2021
```

### Data Proc

Upload the script to GCS:

```bash
gsutil -m cp -r 06_spark_sql.py gs://dtc_data_lake_de-zoomcamp-nytaxi/code/06_spark_sql.py
```

Params for the job:

* `--input_green=gs://dtc_data_lake_de-zoomcamp-nytaxi/pq/green/2021/*/`
* `--input_yellow=gs://dtc_data_lake_de-zoomcamp-nytaxi/pq/yellow/2021/*/`
* `--output=gs://dtc_data_lake_de-zoomcamp-nytaxi/report-2021`


Using Google Cloud SDK for submitting to dataproc
([link](https://cloud.google.com/dataproc/docs/guides/submit-job#dataproc-submit-job-gcloud))

```bash
gcloud dataproc jobs submit pyspark \
    --cluster=de-zoomcamp-cluster \
    --region=europe-west6 \
    gs://dtc_data_lake_de-zoomcamp-nytaxi/code/06_spark_sql.py \
    -- \
        --input_green=gs://dtc_data_lake_de-zoomcamp-nytaxi/pq/green/2020/*/ \
        --input_yellow=gs://dtc_data_lake_de-zoomcamp-nytaxi/pq/yellow/2020/*/ \
        --output=gs://dtc_data_lake_de-zoomcamp-nytaxi/report-2020
```

### Big Query

Upload the script to GCS:

```bash
gsutil -m cp -r 06_spark_sql_big_query.py gs://dtc_data_lake_de-zoomcamp-nytaxi/code/06_spark_sql_big_query.py
```

Write results to big query ([docs](https://cloud.google.com/dataproc/docs/tutorials/bigquery-connector-spark-example#pyspark)):

```bash
gcloud dataproc jobs submit pyspark \
    --cluster=de-zoomcamp-cluster \
    --region=europe-west6 \
    --jars=gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar \
    gs://dtc_data_lake_de-zoomcamp-nytaxi/code/06_spark_sql_big_query.py \
    -- \
        --input_green=gs://dtc_data_lake_de-zoomcamp-nytaxi/pq/green/2020/*/ \
        --input_yellow=gs://dtc_data_lake_de-zoomcamp-nytaxi/pq/yellow/2020/*/ \
        --output=trips_data_all.reports-2020
```

There can be issue with latest Spark version and the Big query connector. Download links to the jar file for respective Spark versions can be found at:
[Spark and Big query connector](https://github.com/GoogleCloudDataproc/spark-bigquery-connector)

**Note**: Dataproc on GCE 2.1+ images pre-install Spark BigQquery connector: [DataProc Release 2.2](https://cloud.google.com/dataproc/docs/concepts/versioning/dataproc-release-2.2). Therefore, no need to include the jar file in the job submission.