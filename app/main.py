from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
from fastapi import Response
import psycopg2
from psycopg2.extras import RealDictCursor
import time

# to launch app, type >uvicorn app.main:app --reload in terminal

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True # specifying value allows the variable to be optional.
    # rating: Optional[int] = None # alternative to optional field

while True:
    try:
        # code to execute SQL statements:
        # bad approach because we hard-code user and psw.
        conn = psycopg2.connect(host = 'localhost', database = 'fastapi', 
            user = 'postgres', password = '0000', cursor_factory=RealDictCursor)
        cursor = conn.cursor() 
        print("Database connection was successful!")
        break
    except Exception as error:
        print("Connecting to database failed.")
        print("Error: ", error)
        time.sleep(2)

# variable that stores the posts we create and save.
# array of dictionaries.
my_posts = [{"title" : "title_1", "content": "content_1", "id": 1},
            {"title" : "title_2", "content": "content_2", "id": 2}]


# function to find post by id:
def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


@app.get("/")
async def root():
    return {"message": "Welcome to my new api"}

# method to get posts:
@app.get("/posts")
def get_posts():
    # SQL statement to get the posts table from postgres:
    cursor.execute("""SELECT * FROM posts""")

    # saving the output in posts:
    posts = cursor.fetchall() # command to actually run the SQL query
    return {"data" : posts}



# method to create new posts
@app.post("/posts", status_code= status.HTTP_201_CREATED) # we specify also the status
def create_posts(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) 
                   VALUES (%s, %s, %s) 
                   RETURNING *""",
    (post.title, post.content, post.published))
    new_post = cursor.fetchone()

    # commit changes to the database leveraging connection:
    conn.commit() # this saves changes to database.
    return {"data" : new_post} 

# function to retrieve specific post: important to place it at the bottom.
# because path parameter can create conflicts when looking for variables.
@app.get("/posts/{id}") # user provides the id from the URL
def get_post(id: int, response: Response): #  {id} is a path parameter
    # id: int provides validation. Checks that id is integer, and
    # converts it to integer.
    cursor.execute("""SELECT * from posts WHERE id = %s """, str(id))
    # we need to re-convert the id to string, to pass it to cursor.execute.
    post = cursor.fetchone()
    if not post: # if not found, return 404.
        # we control the status code of the response
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f"post with id: {id} was not found!")

    return{"post_detail" : post}
# a path parameter will always be returned as a string.

# delete a post: status code of 204 for deletion
@app.delete("/posts/{id}",  status_code= status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    
    cursor.execute("""DELETE FROM posts WHERE id = %s
                   returning * """, str(id))
    deleted_post = cursor.fetchone()
    conn.commit() # committing deletion
    if deleted_post == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f"post with id {id} does not exist!")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# put request: all fields are needed for update.
@app.put("/posts/{id}")
def update_post(id: int, post: Post):

    # update SQL query
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s 
                   WHERE id = %s 
                   RETURNING *""",
                   (post.title, post.content, post.published, str(id)))
    
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= f"post with id {id} does not exist!")
    
    return{'data' : updated_post}