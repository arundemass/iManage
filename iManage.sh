mysql -u root -e "DROP DATABASE IF EXISTS docker_ui";
mysql -u root -e "DROP DATABASE IF EXISTS NFV_Dev";
mysql -u root -e "CREATE DATABASE docker_ui";
mysql -u root -e "CREATE DATABASE NFV_Dev";
mysql -u root docker_ui < /home/ubuntu/docker_ui_project/SQL_DUMP.sql
mysql -u root -e "GRANT USAGE ON *.* TO 'docker_ui'@'localhost'";
mysql -u root -e "DROP USER 'docker_ui'@'localhost'";
mysql -u root -e "CREATE USER 'docker_ui'@'localhost' IDENTIFIED BY 'password-1'";
mysql -u root -e "GRANT ALL PRIVILEGES ON *.* TO 'docker_ui'@'localhost' WITH GRANT OPTION";
mysql -u root -e "GRANT USAGE ON *.* TO 'nfv_user'@'localhost'";
mysql -u root -e "DROP USER 'nfv_user'@'localhost'";
mysql -u root -e "CREATE USER 'nfv_user'@'localhost' IDENTIFIED BY 'password-1'";
mysql -u root -e "GRANT ALL PRIVILEGES ON *.* TO 'nfv_user'@'localhost' WITH GRANT OPTION";
nohup python /home/ubuntu/docker_ui_project/docker_ui/manage.py runserver 0.0.0.0:8765 &
