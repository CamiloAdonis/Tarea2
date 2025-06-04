services:
  mongo:
    image: mongo:5.0
    container_name: mongo_waze
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  scraper:
    build:
      context: ./scraper
      dockerfile: Dockerfile
    container_name: waze_scraper
    depends_on:
      - mongo
    environment:
      - MONGO_HOST=mongo
      - MONGO_PORT=27017
      - META=10000
      - DELAY=5
    restart: unless-stopped

  filtering:
    build:
      context: ./filtering
      dockerfile: Dockerfile
    container_name: waze_filter
    depends_on:
      - mongo
    environment:
      - MONGO_HOST=mongo
      - MONGO_PORT=27017
    volumes:
      - ./data:/data
    command: ["python", "filter.py"]
    restart: "no"

  pig_processing:
    build:
      context: ./pig_processing
      dockerfile: Dockerfile
    container_name: hadoop_pig
    depends_on:
      - filtering
      - mongo
    volumes:
      - ./data:/data
    ports:
      - "9000:9000"
      - "50070:50070"
      - "9870:9870"
      - "8088:8088"
      - "22:22" 
    environment:
      - HDFS_NAMENODE_USER=root
      - HDFS_DATANODE_USER=root
      - YARN_RESOURCEMANAGER_USER=root
      - YARN_NODEMANAGER_USER=root
    restart: "no"

volumes:
  mongo_data:
