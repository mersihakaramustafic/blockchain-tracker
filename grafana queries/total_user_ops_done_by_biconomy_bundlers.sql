SELECT 
  count(bt.user_op_hash) AS "Number of UserOps"
FROM 
  blockchain_tracker AS bt
JOIN biconomy_bundlers AS bb ON lower(bt.from_address) = lower(bb.address)