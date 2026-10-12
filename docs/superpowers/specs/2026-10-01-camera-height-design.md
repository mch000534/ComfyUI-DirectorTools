# Camera height

User approved a height slider that moves the camera above/below the panorama sphere center. A single panorama has no depth; this models an inward-facing unit sphere, not a reconstructed scene. Existing yaw/pitch/zoom controls remain.

Append optional `camera_height` after projection: FLOAT -0.8..0.8, default 0, slider. Units are sphere radii; positive is world up, independent of pitch/yaw. Flat mode ignores height. Legacy API and six/seven-widget workflows default to zero. Reset framing resets height too.

Normalize the perspective ray d, origin o=(0,h,0). Solve the positive intersection t=-h*d.y+sqrt(1-h*h+(h*d.y)^2). Sphere point p=o+t*d; derive wrapped longitude and clamped latitude from p. Use identical math in Python scalar reference, PyTorch sampler and WebGL2 shader. At h=0 preserve existing geometry. Limit height inside sphere so every ray intersects and results stay finite.

Preview, output and serialized workflow share height. Status shows height in sphere mode. Tests cover positive/negative central rays, tilted/off-axis rays, wrapped seams, bounds, zero-height compatibility, tensor versus scalar sampling, shader pixel agreement, reset and workflow reload. No new dependencies or host API changes.
