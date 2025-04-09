#!/bin/bash

# Лог-файл
LOG_FILE="/home/USERNAME/dashbord/error.log"
LOG_DIR=$(dirname "$LOG_FILE")

# Создание директории для лог-файла, если она не существует
if [ ! -d "$LOG_DIR" ]; then
    echo "Создание директории для лог-файла: $LOG_DIR"
    mkdir -p "$LOG_DIR" || { echo "Не удалось создать директорию для лог-файла" >&2; exit 1; }
fi

# Очистка лог-файла
echo "Очистка лог-файла"
> $LOG_FILE || { echo "Не удалось очистить лог-файл" >&2; exit 1; }

# Функция для логирования ошибок
log_error() {
    echo "$(date) - $1" >> $LOG_FILE
}

# Проверка на права root
if [[ $EUID -ne 0 ]]; then
   echo "Этот скрипт должен быть запущен с правами root" | tee -a $LOG_FILE
   exit 1
fi

# apt update & upgrade
echo "Выполняется обновление системы..." | tee -a $LOG_FILE
if ! apt update && apt upgrade -y; then
    log_error "Ошибка при обновлении системы"
fi

# Проверка и монтирование CIFS
echo "Проверка папки /home/USERNAME/disk-z..." | tee -a $LOG_FILE
if [ -d "/home/USERNAME/disk-z" ]; then
    if [ -z "$(ls -A /home/USERNAME/disk-z)" ]; then
        echo "Папка пуста. Монтирование CIFS..." | tee -a $LOG_FILE
        if ! mount.cifs //192.168.0.1/files /home/USERNAME/disk-z -o user=login,pass=password; then
            log_error "Ошибка при монтировании CIFS"
            mount.cifs //192.168.0.1/files /home/USERNAME/disk-z -o user=login,pass=password 2>&1 | tee -a $LOG_FILE
        fi
    fi
else
    log_error "Папка /home/USERNAME/disk-z не существует"
fi

# Проверка и монтирование CIFS
echo "Проверка папки /home/USERNAME/dashbord/disk-z..." | tee -a $LOG_FILE
if [ -d "/home/USERNAME/dashbord/disk-z" ]; then
    if [ -z "$(ls -A /home/USERNAME/dashbord/disk-z)" ]; then
        echo "Папка пуста. Монтирование CIFS..." | tee -a $LOG_FILE
        if ! mount.cifs //192.168.0.1/files /home/USERNAME/dashbord/disk-z -o user=login,pass=password; then
            log_error "Ошибка при монтировании CIFS"
            mount.cifs //192.168.0.1/files /home/USERNAME/dashbord/disk-z -o user=login,pass=password 2>&1 | tee -a $LOG_FILE
        fi
    fi
else
    log_error "Папка /home/USERNAME/dashbord/disk-z не существует"
fi

# Проверка и обновление репозитория git
echo "Проверка git репозитория..." | tee -a $LOG_FILE
if cd /home/USERNAME/dashbord; then
    if ! git pull; then
        echo "Конфликт в git. Выполняется git stash..." | tee -a $LOG_FILE
        if ! git stash && git pull; then
            log_error "Ошибка при выполнении git pull после git stash"
            git stash 2>&1 | tee -a $LOG_FILE
            git pull 2>&1 | tee -a $LOG_FILE
        fi
    fi
else
    log_error "Ошибка: не удалось перейти в директорию /home/USERNAME/dashbord"
fi

# Очистка Docker
echo "Очистка Docker..." | tee -a $LOG_FILE
if ! docker rm $(docker ps -a -q) -f; then
    log_error "Ошибка при удалении контейнеров Docker"
    docker rm $(docker ps -a -q) -f 2>&1 | tee -a $LOG_FILE
fi
if ! docker rmi $(docker images -a -q) -f; then
    log_error "Ошибка при удалении образов Docker"
    docker rmi $(docker images -a -q) -f 2>&1 | tee -a $LOG_FILE
fi
if ! docker system prune -a -f; then
    log_error "Ошибка при очистке системы Docker"
    docker system prune -a -f 2>&1 | tee -a $LOG_FILE
fi

# Очистка /var/log
echo "Очистка /var/log..." | tee -a $LOG_FILE
if ! rm -rf /var/log/*; then
    log_error "Ошибка при очистке /var/log"
    rm -rf /var/log/* 2>&1 | tee -a $LOG_FILE
fi

# Docker Compose
echo "Запуск docker-compose..." | tee -a $LOG_FILE
if cd /home/USERNAME/dashbord; then
    if [ -f docker-compose.yml ]; then
        if ! docker-compose up --force-recreate --build -d; then
            log_error "Ошибка при запуске docker-compose"
            docker-compose up --force-recreate --build -d 2>&1 | tee -a $LOG_FILE
        fi
    else
        log_error "Файл docker-compose.yml не найден в /home/USERNAME/dashbord"
    fi
else
    log_error "Ошибка: не удалось перейти в директорию /home/USERNAME/dashbord"
fi