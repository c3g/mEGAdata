/*
 * transmutation.sql
 *
 */

rename table `experiment_metadata` to `experiment_metadata_old`;

drop table if exists `experiment_property`;
create table `experiment_property` (
  `id`                  int(11) NOT NULL AUTO_INCREMENT,
  `property`            varchar(100) DEFAULT NULL,
  `type`                set('string','int','float','text','uri') DEFAULT NULL,
  `is_exported_to_ega`  tinyint(1) NOT NULL,
  primary key (`id`)
);

drop table if exists `experiment_metadata`;
create table `experiment_metadata` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dataset_id` int(11) NOT NULL,
  `experiment_property_id` int(11) NOT NULL,
  `value` text,
  primary key (`id`),
  KEY `fk_experiment_metadata_dataset1_idx` (`dataset_id`),
  KEY `fk_experiment_metadata_experiment_property1_idx` (`experiment_property_id`),
  CONSTRAINT `fk_experiment_metadata_dataset1` FOREIGN KEY (`dataset_id`) REFERENCES `dataset` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_experiment_metadata_experiment_property1` FOREIGN KEY (`experiment_property_id`) REFERENCES `experiment_property` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
);

-- Loop through each row to fill the metadata
drop procedure if exists transmutation;
delimiter ;;
create procedure transmutation()
begin
declare dataset_length int default 0;
declare attributes_length int default 0;
declare i int default 0;
declare j int default 0;
declare current_dataset_id int default 0;
declare metadata_set_id int default 0;
declare attribute_name varchar(100) default '';
declare attribute_value text default '';
declare property_id int default NULL;

select count(*) from `dataset` into dataset_length;
set i = 0;
while i < dataset_length do

  select id from `dataset` limit i, 1
    into current_dataset_id;
  select experiment_metadata_set_id from `dataset` limit i, 1
    into metadata_set_id;

  select count(*)
  from `experiment_metadata_old`
  where experiment_metadata_set_id = metadata_set_id
    into attributes_length;

  set j = 0;
  while j < attributes_length do

    select lower(`attribute`) from `experiment_metadata_old` limit j, 1
      into attribute_name;
    select `value` from `experiment_metadata_old` limit j, 1
      into attribute_value;

    set property_id = null;
    select `id` from `experiment_property` where lower(property) = attribute_name
      into property_id;

    if (property_id is null) then
        insert into `experiment_property` (`property`, `type`, `is_exported_to_ega`)
          values (attribute_name, 'text', 0);
        select `id` from `experiment_property` where lower(property) = attribute_name
          into property_id;
    end if;

    insert into `experiment_metadata` (`dataset_id`, `experiment_property_id`, `value`)
      values (current_dataset_id, property_id, attribute_value);

    set j = j + 1;
  end while;

  set i = i + 1;
end while;
end;
;;
delimiter ;
call transmutation();
drop procedure transmutation;

-- Drop unused tables & columns
alter table `dataset` drop column `experiment_metadata_set_id`;
drop table `experiment_metadata_old`;
drop table `experiment_metadata_set`;
