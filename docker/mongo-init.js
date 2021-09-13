db.createUser(
    {
        user: "smv-local-user",
        pwd: "smv-local-password",
        roles: [
            {
                role: "dbOwner",
                db: "smv-local"
            }
        ]
    }
);
