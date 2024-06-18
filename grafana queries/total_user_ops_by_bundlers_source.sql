SELECT 
  count(bt.user_op_hash) AS "Number of UserOps",
  case when bb.address is not null 
    then 'Biconomy Bundlers'
  else 'Other Bundlers'
  end as category
FROM 
  blockchain_tracker AS bt
LEFT JOIN biconomy_bundlers AS bb ON lower(bt.from_address) = lower(bb.address)
GROUP BY
  category