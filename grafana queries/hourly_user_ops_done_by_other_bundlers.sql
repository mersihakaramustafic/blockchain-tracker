SELECT 
  date_trunc('hour', to_timestamp(bt.timestamp)) AS hour,
  count(bt.user_op_hash) AS "Number of UserOps"
FROM 
  blockchain_tracker AS bt
LEFT JOIN biconomy_bundlers AS bb ON bt.from_address = bb.address
WHERE bb.address IS NULL
GROUP BY 
  hour
ORDER BY
  hour