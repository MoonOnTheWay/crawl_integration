import mysql.connector

mydb = mysql.connector.connect(
	  host="128.111.54.55",
	  user="muxu",
	  passwd="8054552162",
	  database="moon_master_project",
	  charset='utf8mb4'
	)
mycursor = mydb.cursor()

def get_relevant_blog_ids(arxiv_id):
	sql = "SELECT blog_id \
			FROM blogs_arxivs \
			WHERE arxiv_id = %s"
	mycursor.execute(sql, (arxiv_id,))
	results = mycursor.fetchall()
	return results

def main():
	arxiv_id = '0705.2011'
	blog_ids = get_relevant_blog_ids(arxiv_id)
	print blog_ids

main()