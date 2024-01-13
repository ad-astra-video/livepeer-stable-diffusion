const Ticket {
    Recipient: "0x000parseBase64(params["recipient"]),
    Sender: accounts[0],
    FaceValue: parseBigInt(params["face_value"]),
    WinProb: parseBigInt(params["win_prob"]),
    SenderNonce: BigInt(nonce),
    RecipientRandHash: parseBase64(params["recipient_rand_hash"]),
    CreationRound: BigInt(1)
    AuxData: { 
               CreationRound: BigInt(params["expiration_params"]["creation_round"]),
               CreationRoundBlockHash: parseBase64(params["expiration_params"]["creation_round_block_hash"]),
             },
    };