set -e
test -e "./.env" || { cp .env.example .env; };
export $(egrep -v '^#' .env | xargs)
export COMPOSE_COMMAND="docker-compose"
export PROJECT_PREFIX="ds-calendar"
if ! command -v docker-compose 2>&1 >/dev/null
  then
    COMPOSE_COMMAND="docker compose"
fi

if [ "$1" == "make" ];
  then
    if [ "$2" == "env" ];
        then
            cp .env.example .env
    fi
fi

if [ "$1" == "up" ];
  then
      ${COMPOSE_COMMAND} -p ${PROJECT_PREFIX} up -d;
fi
if [ "$1" == "down" ];
  then
    ${COMPOSE_COMMAND} -p ${PROJECT_PREFIX} down
fi

