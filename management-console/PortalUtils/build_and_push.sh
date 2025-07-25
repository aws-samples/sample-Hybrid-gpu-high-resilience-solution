repo_name=hybrid-gpu-healthcheck
# region=$(aws configure get region)
region=us-east-1

account=$(aws sts get-caller-identity --query Account --output text)

fullname="${account}.dkr.ecr.${region}.amazonaws.com/${repo_name}:latest"

# If the repository doesn't exist in ECR, create it.

aws ecr describe-repositories --region $region --repository-names "${repo_name}" > /dev/null 2>&1
if [ $? -ne 0 ]
then
echo "create repository:" "${repo_name}"
aws ecr create-repository --region $region  --repository-name "${repo_name}" > /dev/null
fi

#load public ECR image
#aws ecr-public get-login-password --region $region | docker login --username AWS --password-stdin public.ecr.aws

aws ecr get-login-password --region ${region}|docker login --username AWS --password-stdin ${fullname}

docker build -t ${repo_name} -f Dockerfile .

docker tag ${repo_name} ${fullname}
docker push ${fullname}

echo $fullname