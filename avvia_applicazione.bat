@echo off
echo ===================================================
echo Avvio dell'applicazione Sustainable Food Supply Chain
echo ===================================================

set PROJECT_DIR=%~dp0
set ON_CHAIN_DIR=%PROJECT_DIR%on_chain
set OFF_CHAIN_DIR=%PROJECT_DIR%off_chain

echo.
echo Passo 0: Verifica e installazione di Hardhat...
echo.
cd /d %ON_CHAIN_DIR%

if not exist node_modules\hardhat (
    echo Hardhat non trovato. Installazione in corso...
    call npm install --save-dev hardhat
    if %ERRORLEVEL% NEQ 0 (
        echo Errore durante l'installazione di Hardhat!
        pause
        exit /b 1
    )
    echo Hardhat installato con successo.
) else (
    echo Hardhat già installato.
)

echo.
echo Passo 1: Avvio del nodo Hardhat in un terminale separato...
echo.
start "Hardhat Node" cmd /k "cd /d %ON_CHAIN_DIR% && npx hardhat node"

echo Attesa avvio del nodo Hardhat (10 secondi)...
timeout /t 10 /nobreak > nul

echo.
echo Passo 2: Compilazione dei contratti...
echo.
cd /d %ON_CHAIN_DIR%
call npx hardhat compile
if %ERRORLEVEL% NEQ 0 (
    echo Errore durante la compilazione dei contratti!
    pause
    exit /b 1
)

echo.
echo Passo 3: Deployment dei contratti...
echo.
cd /d %ON_CHAIN_DIR%
call npx hardhat run scripts/deploy.js --network localhost
if %ERRORLEVEL% NEQ 0 (
    echo Errore durante il deployment dei contratti!
    pause
    exit /b 1
)

echo.
echo Passo 4: Avvio dell'applicazione...
echo.
cd /d %OFF_CHAIN_DIR%
python main.py

echo.
echo ===================================================
echo Applicazione terminata!
echo ===================================================
echo.
echo Ricorda di chiudere il terminale del nodo Hardhat.
echo.

pause
