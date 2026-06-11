
local closeloadingscreen = false

AddEventHandler("playerSpawned", function()
    if not closeloadingscreen then
        ShutdownLoadingScreenNui()
        closeloadingscreen = true
            DoScreenFadeOut(0)
            Wait(2000)
            DoScreenFadeIn(2500)
    end
end)