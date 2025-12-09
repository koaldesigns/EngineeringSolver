# Test Authentication API Endpoints
# Run with: .\test_auth_api.ps1

$BaseUrl = "http://localhost:8000"
$passed = 0
$failed = 0

function Test-Endpoint {
    param (
        [string]$Name,
        [string]$Method,
        [string]$Url,
        [object]$Body,
        [int]$ExpectedStatus,
        [hashtable]$Headers
    )
    
    try {
        $params = @{
            Uri = $Url
            Method = $Method
            ContentType = "application/json"
            ErrorAction = "Stop"
        }
        
        if ($null -ne $Body) {
            $params.Body = ($Body | ConvertTo-Json -Depth 10)
        }
        
        if ($null -ne $Headers) {
            $params.Headers = $Headers
        }
        
        $response = Invoke-WebRequest @params
        $status = $response.StatusCode
        
        if ($status -eq $ExpectedStatus) {
            Write-Host "[PASS] $Name" -ForegroundColor Green
            return @{ Passed = $true; Response = ($response.Content | ConvertFrom-Json) }
        } else {
            Write-Host "[FAIL] $Name - Expected $ExpectedStatus, got $status" -ForegroundColor Red
            return @{ Passed = $false; Response = $null }
        }
    }
    catch {
        $status = $_.Exception.Response.StatusCode.value__
        if ($status -eq $ExpectedStatus) {
            Write-Host "[PASS] $Name (expected error $ExpectedStatus)" -ForegroundColor Green
            return @{ Passed = $true; Response = $null }
        } else {
            Write-Host "[FAIL] $Name - Error: $_" -ForegroundColor Red
            return @{ Passed = $false; Response = $null }
        }
    }
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "         AUTHENTICATION API TESTS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health endpoint
$result = Test-Endpoint -Name "Health endpoint" -Method "GET" -Url "$BaseUrl/health" -ExpectedStatus 200
if ($result.Passed) { $passed++ } else { $failed++ }

# Test 2: Root endpoint
$result = Test-Endpoint -Name "Root endpoint" -Method "GET" -Url "$BaseUrl/" -ExpectedStatus 200
if ($result.Passed) { $passed++ } else { $failed++ }

# Test 3: Solve endpoint still works
$solveBody = @{
    equations = @("x = 5", "y = x * 2")
    angle_unit = "deg"
}
$result = Test-Endpoint -Name "Solve endpoint (regression)" -Method "POST" -Url "$BaseUrl/api/solve" -Body $solveBody -ExpectedStatus 200
if ($result.Passed) { $passed++ } else { $failed++ }

# Test 4: Registration with invalid token fails
$regBody = @{
    username = "testuser"
    password = "testpass"
    token = "INVALID-TOKEN"
}
$result = Test-Endpoint -Name "Registration with invalid token fails" -Method "POST" -Url "$BaseUrl/api/auth/register" -Body $regBody -ExpectedStatus 400
if ($result.Passed) { $passed++ } else { $failed++ }

# Test 5: Custom tabs without auth returns empty
$result = Test-Endpoint -Name "Custom tabs without auth" -Method "GET" -Url "$BaseUrl/api/custom-tabs" -ExpectedStatus 200
if ($result.Passed -and $result.Response.logged_in -eq $false) { 
    $passed++ 
    Write-Host "       -> Returns logged_in=false as expected" -ForegroundColor Gray
} else { 
    $failed++ 
}

# Test 6: Save tabs requires auth (401 or 422)
$tabsBody = @{ tabs = @() }
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/api/custom-tabs" -Method POST -Body ($tabsBody | ConvertTo-Json) -ContentType "application/json" -ErrorAction Stop
    Write-Host "[FAIL] Saving tabs without auth should fail" -ForegroundColor Red
    $failed++
}
catch {
    $status = $_.Exception.Response.StatusCode.value__
    if ($status -eq 401 -or $status -eq 403) {
        Write-Host "[PASS] Save tabs requires auth (got $status)" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "[FAIL] Save tabs - unexpected status $status" -ForegroundColor Red
        $failed++
    }
}

# Test 7: Preferences requires auth
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/api/preferences" -Method GET -ErrorAction Stop
    Write-Host "[FAIL] Preferences without auth should fail" -ForegroundColor Red
    $failed++
}
catch {
    $status = $_.Exception.Response.StatusCode.value__
    if ($status -eq 401 -or $status -eq 403) {
        Write-Host "[PASS] Preferences requires auth (got $status)" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "[FAIL] Preferences - unexpected status $status" -ForegroundColor Red
        $failed++
    }
}

# Test 8: Admin endpoints require auth
try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/api/admin/users" -Method GET -ErrorAction Stop
    Write-Host "[FAIL] Admin endpoint without auth should fail" -ForegroundColor Red
    $failed++
}
catch {
    $status = $_.Exception.Response.StatusCode.value__
    if ($status -eq 401 -or $status -eq 403) {
        Write-Host "[PASS] Admin endpoint requires auth (got $status)" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "[FAIL] Admin - unexpected status $status" -ForegroundColor Red
        $failed++
    }
}

# Test 9: Login with invalid credentials
$loginBody = @{
    username = "nonexistent"
    password = "wrongpass"
}
$result = Test-Endpoint -Name "Login with invalid credentials fails" -Method "POST" -Url "$BaseUrl/api/auth/login" -Body $loginBody -ExpectedStatus 401
if ($result.Passed) { $passed++ } else { $failed++ }

Write-Host ""
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "         FULL AUTHENTICATION FLOW TEST" -ForegroundColor Cyan
Write-Host "------------------------------------------------------------" -ForegroundColor Cyan

$uniqueId = [DateTimeOffset]::Now.ToUnixTimeSeconds()
$testUsername = "flowtest_$uniqueId"
$testPassword = "testpass123"

# Step 1: Register new user
$regBody = @{
    username = $testUsername
    password = $testPassword
    token = "ENG-9F5D1-BT7ZC"
}

try {
    $response = Invoke-WebRequest -Uri "$BaseUrl/api/auth/register" -Method POST -Body ($regBody | ConvertTo-Json) -ContentType "application/json" -ErrorAction Stop
    $regData = $response.Content | ConvertFrom-Json
    
    if ($regData.access_token) {
        Write-Host "[PASS] User registration succeeded" -ForegroundColor Green
        $passed++
        $token = $regData.access_token
        $headers = @{ "Authorization" = "Bearer $token" }
        
        # Step 2: Test /me endpoint
        $response = Invoke-WebRequest -Uri "$BaseUrl/api/auth/me" -Method GET -Headers $headers -ErrorAction Stop
        $meData = $response.Content | ConvertFrom-Json
        if ($meData.username -eq $testUsername) {
            Write-Host "[PASS] /me endpoint returns correct user" -ForegroundColor Green
            $passed++
        } else {
            Write-Host "[FAIL] /me returned wrong username" -ForegroundColor Red
            $failed++
        }
        
        # Step 3: Test preferences
        $response = Invoke-WebRequest -Uri "$BaseUrl/api/preferences" -Method GET -Headers $headers -ErrorAction Stop
        Write-Host "[PASS] Get preferences works" -ForegroundColor Green
        $passed++
        
        # Step 4: Update preferences
        $prefsBody = @{
            theme_mode = "light"
            accent_hue = 180
        }
        $response = Invoke-WebRequest -Uri "$BaseUrl/api/preferences" -Method PUT -Headers $headers -Body ($prefsBody | ConvertTo-Json) -ContentType "application/json" -ErrorAction Stop
        Write-Host "[PASS] Update preferences works" -ForegroundColor Green
        $passed++
        
        # Step 5: Test custom tabs with auth
        $response = Invoke-WebRequest -Uri "$BaseUrl/api/custom-tabs" -Method GET -Headers $headers -ErrorAction Stop
        $tabsData = $response.Content | ConvertFrom-Json
        if ($tabsData.logged_in -eq $true) {
            Write-Host "[PASS] Custom tabs shows logged_in=true" -ForegroundColor Green
            $passed++
        } else {
            Write-Host "[FAIL] Custom tabs should show logged_in=true" -ForegroundColor Red
            $failed++
        }
        
        # Step 6: Save custom tabs
        $testTabs = @{
            tabs = @(
                @{
                    id = "test_tab_1"
                    name = "Test Tab"
                    icon = "T"
                    equationSets = @(
                        @{
                            id = "eq_1"
                            title = "Test Equations"
                            description = "Test description"
                            equations = "x = 5`ny = x * 2"
                        }
                    )
                }
            )
        }
        $response = Invoke-WebRequest -Uri "$BaseUrl/api/custom-tabs" -Method POST -Headers $headers -Body ($testTabs | ConvertTo-Json -Depth 10) -ContentType "application/json" -ErrorAction Stop
        Write-Host "[PASS] Save custom tabs works" -ForegroundColor Green
        $passed++
        
        # Step 7: Verify tabs saved
        $response = Invoke-WebRequest -Uri "$BaseUrl/api/custom-tabs" -Method GET -Headers $headers -ErrorAction Stop
        $savedTabs = ($response.Content | ConvertFrom-Json).tabs
        if ($savedTabs.Count -eq 1 -and $savedTabs[0].name -eq "Test Tab") {
            Write-Host "[PASS] Tabs saved and retrieved correctly" -ForegroundColor Green
            $passed++
        } else {
            Write-Host "[FAIL] Tabs not saved correctly" -ForegroundColor Red
            $failed++
        }
        
        # Step 8: Token refresh
        $response = Invoke-WebRequest -Uri "$BaseUrl/api/auth/refresh" -Method POST -Headers $headers -ErrorAction Stop
        $refreshData = $response.Content | ConvertFrom-Json
        if ($refreshData.access_token) {
            Write-Host "[PASS] Token refresh works" -ForegroundColor Green
            $passed++
        } else {
            Write-Host "[FAIL] Token refresh failed" -ForegroundColor Red
            $failed++
        }
        
    } else {
        Write-Host "[FAIL] Registration didn't return access_token" -ForegroundColor Red
        $failed++
    }
}
catch {
    Write-Host "[FAIL] Registration failed: $_" -ForegroundColor Red
    $failed++
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "         RESULTS: $passed passed, $failed failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Yellow" })
Write-Host "============================================================" -ForegroundColor Cyan
