$BaseUrl = "https://mailmind-sandbox-api.onrender.com"
$Passed = 0
$Failed = 0
$Warnings = 0

Write-Host "`n========== MAILMIND API TEST RUN (V2) ==========" -ForegroundColor Cyan
Write-Host "API: $BaseUrl"

function Test-Health {
    Write-Host "`n----- HEALTH CHECK -----" -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/health" -Method GET -TimeoutSec 30
        $response | ConvertTo-Json -Depth 5
        if ($response.status -eq "healthy") {
            Write-Host "HEALTH: PASS" -ForegroundColor Green
            $script:Passed++
        } else {
            Write-Host "HEALTH: FAIL (unexpected status)" -ForegroundColor Red
            $script:Failed++
        }
    } catch {
        Write-Host "HEALTH: FAIL ($($_.Exception.Message))" -ForegroundColor Red
        $script:Failed++
    }
}

function Test-EmailCase {
    param(
        [string]$Name,
        [string]$Sender,
        [string]$Subject,
        [string]$Body,
        [string]$ExpectedCategory,
        [string]$ExpectedPriority,
        [bool]$ExpectedAutomated
    )

    Write-Host "`n----- $Name -----" -ForegroundColor Yellow
    try {
        $payload = @{
            sender  = $Sender
            subject = $Subject
            body   = $Body
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri "$BaseUrl/analyze" -Method POST `
            -ContentType "application/json" -Body $payload -TimeoutSec 60

        $response | ConvertTo-Json -Depth 5

        $issues = @()
        if ($response.category -ne $ExpectedCategory) {
            $issues += "category expected '$ExpectedCategory', got '$($response.category)'"
        }
        if ($response.priority -ne $ExpectedPriority) {
            $issues += "priority expected '$ExpectedPriority', got '$($response.priority)'"
        }
        if ([bool]$response.automated -ne $ExpectedAutomated) {
            $issues += "automated expected '$ExpectedAutomated', got '$($response.automated)'"
        }
        if ([string]::IsNullOrWhiteSpace([string]$response.reply_draft)) {
            $issues += "missing reply_draft"
        }
        if ([string]::IsNullOrWhiteSpace([string]$response.provider)) {
            $issues += "missing provider"
        }

        if ($issues.Count -eq 0) {
            Write-Host "${Name}: PASS" -ForegroundColor Green
            $script:Passed++
        } else {
            Write-Host "${Name}: FAIL ($($issues -join '; '))" -ForegroundColor Red
            $script:Failed++
        }

        if ($response.ai_warning) {
            Write-Host "AI WARNING: $($response.ai_warning)" -ForegroundColor DarkYellow
            $script:Warnings++
        }
        if ($response.provider -eq "Rules fallback") {
            Write-Host "NOTE: Response used fallback rules instead of Gemini." -ForegroundColor DarkYellow
        }
    } catch {
        Write-Host "${Name}: FAIL (request error: $($_.Exception.Message))" -ForegroundColor Red
        $script:Failed++
    }
}

Test-Health

Test-EmailCase -Name "Job Email" `
    -Sender "recruiter@example.com" `
    -Subject "Software Engineer Interview Opportunity" `
    -Body "We would like to schedule an interview for our software engineering role. Please reply with your availability." `
    -ExpectedCategory "Job" -ExpectedPriority "High" -ExpectedAutomated $false

Test-EmailCase -Name "Urgent Email" `
    -Sender "support@example.com" `
    -Subject "Urgent: Account issue needs attention today" `
    -Body "Your account issue is unresolved and requires action before today's deadline. Please respond as soon as possible." `
    -ExpectedCategory "Complaint" -ExpectedPriority "High" -ExpectedAutomated $false

Test-EmailCase -Name "Promotion Email" `
    -Sender "offers@example.com" `
    -Subject "Limited time offer: 50% off" `
    -Body "Subscribe now and enjoy our limited-time promotional discount. Click to shop today." `
    -ExpectedCategory "Promotion" -ExpectedPriority "Low" -ExpectedAutomated $true

Test-EmailCase -Name "Personal Email" `
    -Sender "friend@example.com" `
    -Subject "Let's catch up soon!" `
    -Body "Hey! It has been a while. Want to meet for coffee this weekend and catch up?" `
    -ExpectedCategory "Personal" -ExpectedPriority "Normal" -ExpectedAutomated $false

Write-Host "`n========== SUMMARY ==========" -ForegroundColor Cyan
Write-Host "Passed:   $Passed" -ForegroundColor Green
Write-Host "Failed:   $Failed" -ForegroundColor Red
Write-Host "Warnings: $Warnings" -ForegroundColor DarkYellow
Write-Host "Total:   $($Passed + $Failed)"
if ($Failed -eq 0) {
    Write-Host "API functional checks passed. Review warnings separately." -ForegroundColor Green
} else {
    Write-Host "Some functional checks failed. Copy this output for debugging." -ForegroundColor Red
}
