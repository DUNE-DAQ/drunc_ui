# Kubernetes configuration

This directory contains an exemplar for the deployment of `drunc_ui` in a Kubernetes cluster. It largely follows this [k8 tutorial in Medium], with a couple of changes to work with our specific use case.

This exemplar is NOT meant to be production ready, but rather to inspire how `drunc_ui` could be deployed in a Kubernetes cluster. For it to be useful, other services, like the process manager or the session manager, should be running in the cluseter, as well.

It is NOT meant to be for development, either. Not only it does not include the `drunc` services, but it is also more complicated to work with than `docker compose`.

[k8 tutorial in Medium]: https://tarekeesa7.medium.com/deploying-and-scaling-django-apps-in-kubernetes-k8s-with-postgresql-659e863ef033

## What are these files?

This directory contains several sub-directories each including manisfest files to configure the different components of the cluster:

- `app`: The actual `drunc_ui` application, using `Django`. It also defines a persistent volume to store the static files (html, js, css).
- `db`: A `postgress` database that supports the `Django` app. It also defines a persistent volume where the database is stored.
- `nginx`: The reverse proxy, routing requests from the external world to the `Django` application within the cluster, as well as serving the static files stored in the persistent volume.
- `jobs`: Contains manifests that execute one off tasks, like running migrations and collecting static files. Typically, these need to be run one once at the start and if ever new migrrations need to be applied, or static files collected.

## How do I try it?

This setup has been tested using [Minikube], but it should work in any Kubernetes cluster - hopefully! The specific steps would be:

- [Install Minikube] and follow the instructions within to ensure that the command `kubectl` is available and that you [use the `docker` daemon within the cluster] (for that terminal session).
- From the root directory of the repository, build the `drunc_ui` docker image with `docker build -t drunc_ui_app:latest .` (mind the period at the end of the command). If you are using the `docker` daemon within the cluster, as instructed above, this will make the image available there.
- Apply the configurations to start the different services. The order matters, since some services depend on others. In principle, it would be OK any other other, but dependent services will need to wait until they are ready to be launched.
    - `kubectl apply -f k8s/db`
    - `kubectl apply -f k8s/app`
    - `kubectl apply -f k8s/nginx`
- The pods should all be running, now. You can check with `kubectl get pod -n drunc-ui-app`: there should be three, one per service.
- However, `drunc_ui` will not work, yet, as we have not applied the migrations nor collected the static files. We can do so by running the following jobs - in this order and waiting for them to finish (check the `kubectl get` command above):
    - `kubectl apply -f k8s/jobs/migration-job.yml`
    - `kubectl apply -f k8s/jobs/staticfile-job.yml`

Now things should be ready and accessible from your web browser. To get the URL you need to go, just run `minikube service nginx-service -n drunc-ui-app --url`. We are asking the `nginx-service` because that is the one exposing a port outside of the cluster.

[Minikube]: https://minikube.sigs.k8s.io
[Install Minikube]: https://minikube.sigs.k8s.io/docs/start/
[use the `docker` daemon within the cluster]: https://minikube.sigs.k8s.io/docs/handbook/pushing/#1-pushing-directly-to-the-in-cluster-docker-daemon-docker-env

## Further comments

- If the URL in the last command is not the one included in `k8s/app/app-cm.yml` for `CSRF_TRUSTED_ORIGINS`, replace the old value and re-apply the app.
- You would need to create a superuser. Do so with `kubectl exec -it NAME_OF_DJANGO_APP_POD -n drunc-ui-app -- python manage.py createsuperuser`, where the `NAME_OF_DJANGO_APP_POD` can be found when running
`kubectl get pod -n drunc-ui-app`.
