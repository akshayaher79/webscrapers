from psycopg2 import connect as psql_connect
from psycopg2.extras import Json
import logging


class PostgresPipeline:

    @classmethod
    def from_crawler(cls, crawler):
        dbclient = cls()
        dbclient.dsn = {
            'host': crawler.settings.get('DB_HOST'),
            'port': crawler.settings.get('DB_PORT'),
            'user': crawler.settings.get('DB_USER'),
            'password': crawler.settings.get('DB_PASSWORD'),
            'dbname': crawler.settings.get('DB_NAME')
        }
        dbclient.table =\
            f'public.{crawler.spider.name.replace(".", "_")}'

        return dbclient

    def open_spider(self, spider):
        self.conn = psql_connect(**self.dsn)
        logging.info('DB connection establsihed.')
        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    f"""
                        CREATE TABLE IF NOT EXISTS {self.table} (
                        "content" character varying COLLATE pg_catalog."default" NOT NULL,
                        "website_name" character varying COLLATE pg_catalog."default" NOT NULL,
                        "timestamp" timestamp with time zone,
                        "date_of_scrap" timestamp with time zone,
                        "text" text COLLATE pg_catalog."default" NOT NULL,
                        "url" character varying COLLATE pg_catalog."default",
                        "post_num" character varying COLLATE pg_catalog."default",
                        "extradata" json,
                        CONSTRAINT "{self.table}_pkey" PRIMARY KEY (url, post_num)
                    )"""
                )

    def process_item(self, item, spider):
        item['extradata'] = Json(item['extradata'])

        with self.conn:
            with self.conn.cursor() as cur:
                cur.execute(
                    f"""INSERT INTO {self.table} (
                        content, website_name, timestamp,
                        date_of_scrap, text, url, post_num, extradata
                    ) VALUES (
                        %(content)s, %(website_name)s, %(timestamp)s,
                        %(date_of_scrap)s, %(text)s, %(url)s, %(post_num)s,
                        %(extradata)s
                    )""",
                    item
                )
        return item

    def close_spider(self, spider):
        self.conn.close()
