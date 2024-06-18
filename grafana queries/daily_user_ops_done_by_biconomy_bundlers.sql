SELECT 
  date_trunc('day', to_timestamp(bt.timestamp)) AS day,
  count(bt.user_op_hash) AS "Number of UserOps"
FROM 
  blockchain_tracker AS bt
JOIN biconomy_bundlers AS bb ON lower(bt.from_address) = lower(bb.address)
GROUP BY 
  day
ORDER BY
  day