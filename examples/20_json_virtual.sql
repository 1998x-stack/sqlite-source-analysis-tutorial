SELECT key,value FROM json_each('[10,20,30]') ORDER BY CAST(key AS INTEGER);
