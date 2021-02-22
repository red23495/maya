CREATE TABLE raw_requests
(
    id int PRIMARY KEY auto_increment,
    name varchar(1024),
    META TEXT,
    `GET` TEXT,
    POST TEXT,
    COOKIES varchar(4096),
    REQUEST TEXT,
    method varchar(10),
    data TEXT,
    path varchar(1024),
    raw_post_data TEXT,
    response_content LONGTEXT,
    content_type varchar(512),
    status_code int
);

CREATE TABLE filesystems
(
    id int PRIMARY KEY auto_increment,
    name varchar(1024),
    package_id int
);

CREATE TABLE packages
(
    id int PRIMARY KEY auto_increment,
    parent_package_id int,
    selected int DEFAULT 0,
    dir varchar(1024)
);

CREATE TABLE test_cases
(
    id int PRIMARY KEY auto_increment,
    name varchar(1024),
    selected int DEFAULT 0,
    package_id int
);

CREATE TABLE requests
(
    id int PRIMARY KEY auto_increment,
    raw_request_id int,
    status varchar(100),
    selected int DEFAULT 0,
    test_case_id int
);

CREATE TABLE filesystem_requests
(
    id int PRIMARY KEY auto_increment,
    filesystem_id int,
    raw_request_id int,
    is_processed int DEFAULT 0
);
ALTER TABLE packages ADD execution_order int DEFAULT 0 NULL;
ALTER TABLE requests ADD execution_order int DEFAULT 0 NULL;
ALTER TABLE test_cases ADD execution_order int DEFAULT 0 NULL;

create table play_records
(
  id          int auto_increment
    primary key,
  result      longtext      null,
  recorded_at datetime      null,
  filesystem  varchar(1024) null,
  package     varchar(1024) null
);



