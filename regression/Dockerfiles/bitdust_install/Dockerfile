#
# Dockerfile.py
#
# Copyright (C) 2008-2018 Stanislav Evseev, Veselin Penev  https://bitdust.io
#
# This file (Dockerfile.py) is part of BitDust Software.
#
# BitDust is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BitDust Software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with BitDust Software.  If not, see <http://www.gnu.org/licenses/>.
#
# Please contact us if you have any questions at bitdust.io@gmail.com

ARG  PYTHON_VERSION=2.7.15

FROM python:${PYTHON_VERSION}



RUN apt-get update && apt-get install -y \
    curl openssh-server mosh nano \
 && rm -rf /var/lib/apt/lists/* \
 && pip install virtualenv

RUN mkdir /var/run/sshd \
    && echo 'AuthorizedKeysFile %h/.ssh/authorized_keys' >> /etc/ssh/sshd_config \
    && sed -i 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' /etc/pam.d/sshd \
    && sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config



WORKDIR /app

COPY . /app/bitdust

RUN python /app/bitdust/bitdust.py install

RUN echo '#!/bin/sh\n /root/.bitdust/venv/bin/python /app/bitdust/bitdust.py "$@"' > /bin/bitdust

RUN chmod +x /bin/bitdust



ADD ./regression/ssh/ /app/ssh

EXPOSE 22

CMD /app/ssh/sshd.sh
