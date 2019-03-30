--seed data
INSERT INTO "user"(id,email)
VALUES
 (1,'lzhengem@gmail.com');


Insert into "item"(title, description, cat_id, user_id)
VALUES ('Soccer Ball', 'Ball for kicking',1,1);
Insert into "item"(title, description, cat_id, user_id)
VALUES ('Soccer Net', 'Net for catching soccer ball',1,1);

Insert into "item"(title, description, cat_id, user_id)
VALUES ('Basketball', 'Ball for basketball',2,1);
Insert into "item"(title, description, cat_id, user_id)
VALUES ('Hoop', 'Hoop for basketball',2,1);

Insert into "item"(title, description, cat_id, user_id)
VALUES ('Snowboard', 'Snowboard for shreading snow',5,1);