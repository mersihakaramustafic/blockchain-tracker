SELECT 
  date_trunc('week', to_timestamp(bt.timestamp)) AS week,
  count(bt.user_op_hash) AS "Number of UserOps"
FROM 
  blockchain_tracker AS bt
JOIN biconomy_bundlers AS bb ON lower(bt.from_address) = lower(bb.address)
GROUP BY 
  week
ORDER BY
  week