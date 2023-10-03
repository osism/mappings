ARG PYTHON_VERSION=3.12

ARG CEPH_ANSIBLE_VERSION=pacific
ARG KOLLA_ANSIBLE_VERSION=wallaby
ARG OSISM_ANSIBLE_VERSION=latest

FROM quay.io/osism/ceph-ansible:${CEPH_ANSIBLE_VERSION} as ceph-ansible
FROM quay.io/osism/kolla-ansible:${KOLLA_ANSIBLE_VERSION} as kolla-ansible
FROM quay.io/osism/osism-ansible:${OSISM_ANSIBLE_VERSION} as osism-ansible


FROM python:${PYTHON_VERSION} as builder

COPY --from=ceph-ansible /ansible /ceph-ansible
COPY --from=kolla-ansible /ansible /kolla-ansible
COPY --from=osism-ansible /ansible /osism-ansible
COPY --from=osism-ansible /usr/share/ansible/collections /usr/share/ansible/collections
COPY --from=osism-ansible /usr/share/ansible/roles /usr/share/ansible/roles

COPY . /src
WORKDIR /src

RUN python3 -m pip --no-cache-dir install -U 'pip==21.3.1' 'pipenv==2022.1.8' \
    && pipenv install

CMD ["pipenv", "run", "generate"]
