ARG PYTHON_VERSION=3.14

ARG CEPH_ANSIBLE_VERSION=reef
ARG KOLLA_ANSIBLE_VERSION=2026.1
ARG OSISM_ANSIBLE_VERSION=latest
ARG OSISM_KUBERNETES_VERSION=latest
ARG INVENTORY_RECONCILER_VERSION=latest

FROM registry.osism.tech/osism/ceph-ansible:${CEPH_ANSIBLE_VERSION} as ceph-ansible
FROM registry.osism.tech/osism/kolla-ansible:${KOLLA_ANSIBLE_VERSION} as kolla-ansible
FROM registry.osism.tech/osism/osism-ansible:${OSISM_ANSIBLE_VERSION} as osism-ansible
FROM registry.osism.tech/osism/osism-kubernetes:${OSISM_KUBERNETES_VERSION} as osism-kubernetes
FROM registry.osism.tech/osism/inventory-reconciler:${INVENTORY_RECONCILER_VERSION} as inventory-reconciler


FROM python:${PYTHON_VERSION} as builder

COPY --from=ceph-ansible /ansible /ceph-ansible
COPY --from=kolla-ansible /ansible /kolla-ansible
COPY --from=osism-ansible /ansible /osism-ansible
COPY --from=osism-ansible /usr/share/ansible/collections /usr/share/ansible/collections
COPY --from=osism-ansible /usr/share/ansible/roles /usr/share/ansible/roles
COPY --from=osism-kubernetes /ansible/roles /osism-kubernetes/roles
COPY --from=kolla-ansible /usr/local/share/kolla-ansible/ansible/group_vars /kolla-group_vars
COPY --from=inventory-reconciler /defaults /osism-defaults

COPY . /src
WORKDIR /src

RUN python3 -m pip --no-cache-dir install -U pip pipenv \
    && pipenv install

CMD ["pipenv", "run", "generate"]
