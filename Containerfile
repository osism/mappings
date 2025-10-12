ARG PYTHON_VERSION=3.13

ARG CEPH_ANSIBLE_VERSION=reef
ARG KOLLA_ANSIBLE_VERSION=2025.1
ARG OSISM_ANSIBLE_VERSION=latest

FROM registry.osism.tech/osism/ceph-ansible:${CEPH_ANSIBLE_VERSION} as ceph-ansible
FROM registry.osism.tech/osism/kolla-ansible:${KOLLA_ANSIBLE_VERSION} as kolla-ansible
FROM registry.osism.tech/osism/osism-ansible:${OSISM_ANSIBLE_VERSION} as osism-ansible


FROM python:${PYTHON_VERSION} as builder

COPY --from=ceph-ansible /ansible /ceph-ansible
COPY --from=kolla-ansible /ansible /kolla-ansible
COPY --from=osism-ansible /ansible /osism-ansible
COPY --from=osism-ansible /usr/share/ansible/collections /usr/share/ansible/collections
COPY --from=osism-ansible /usr/share/ansible/roles /usr/share/ansible/roles

COPY . /src
WORKDIR /src

RUN python3 -m pip --no-cache-dir install -U pip pipenv \
    && pipenv install

CMD ["pipenv", "run", "generate"]
