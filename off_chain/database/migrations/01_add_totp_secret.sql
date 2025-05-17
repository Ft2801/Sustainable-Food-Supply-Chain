-- Add TOTP secret column to Credenziali table
ALTER TABLE Credenziali ADD COLUMN totp_secret TEXT;
