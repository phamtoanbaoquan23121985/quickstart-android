package org.aegis.reality

import android.Manifest
import android.content.ComponentName
import android.content.pm.PackageManager
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.assertEquals
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class PermissionSurfaceTest {
    @Test
    fun undeclaredContactsPermissionRemainsDenied() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        assertEquals(
            PackageManager.PERMISSION_DENIED,
            context.checkSelfPermission(Manifest.permission.READ_CONTACTS)
        )
    }

    @Test
    fun harnessComponentsAreNotExported() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val flags = PackageManager.ComponentInfoFlags.of(0)
        val activity = context.packageManager.getActivityInfo(
            ComponentName(context, HarnessActivity::class.java), flags
        )
        val service = context.packageManager.getServiceInfo(
            ComponentName(context, IpcProbeService::class.java), flags
        )
        assertEquals(false, activity.exported)
        assertEquals(false, service.exported)
    }
}
