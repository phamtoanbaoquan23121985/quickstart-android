package org.aegis.reality

import android.os.Build
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class DeviceScopeTest {
    @Test
    fun runsOnlyOnApprovedPixel10TargetsAndAndroid16() {
        val allowed = setOf("blazer", "mustang")
        assertTrue("Unexpected device codename: ${Build.DEVICE}", Build.DEVICE in allowed)
        assertEquals(36, Build.VERSION.SDK_INT)
    }

    @Test
    fun capturesBuildIdentityWithoutCollectingDeviceIdentifiers() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val report = mapOf(
            "device" to Build.DEVICE,
            "manufacturer" to Build.MANUFACTURER,
            "model" to Build.MODEL,
            "api" to Build.VERSION.SDK_INT,
            "fingerprint" to Build.FINGERPRINT,
            "package" to context.packageName
        )
        assertTrue(report["fingerprint"].toString().isNotBlank())
        // Intentionally do not read serial numbers, IMEI, accounts, or secrets.
    }
}
