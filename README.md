# Haj

Something something blahaj frc discord bot

### Database Layout

```
haj.db
│
├─ table 'guilds'
│  │
│  ├─ column 'guild_id' (int, not null, primary key)
│  ├─ column 'task_channel_id' (int)
│  └─ column 'mod_channel_id' (int)
│
└─ table 'admins'
   │
   └─ column 'user_id' (int, not null, primary key)
```

---

[Powered by The Blue Alliance](https://www.thebluealliance.com/)