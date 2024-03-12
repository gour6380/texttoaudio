import Vapor
import Foundation
import PythonKit

struct Config: Codable {
    var speaker_data: String
    var conversation: String
}

func getListOfAudioFiles() throws -> [String] {
    let fileManager = FileManager.default
    let currentDirectoryURL = fileManager.currentDirectoryPath

    guard let files = try? fileManager.contentsOfDirectory(atPath: currentDirectoryURL) else {
        throw Abort(.internalServerError, reason: "Unable to read files in audios directory")
    }

    return files.filter { $0.hasSuffix(".mp3") || $0.hasSuffix(".wav") } // Filter only audio files if needed
}

func routes(_ app: Application) throws {

    let subprocess = Python.import("subprocess")
    let os = Python.import("os")
    let sys = Python.import("sys")
    let pythonQueue = DispatchQueue(label: "python_utils_queue")

    os.chdir("TexttoAudio");

    // Get the current working directory directly, as it's not an Optional
    let cwd = os.getcwd()


    let install_lib = subprocess.run(["pip3", "install", "-e", "."])

    //Check if the command was successful
    if install_lib.returncode == 0 {
        print("Package installed successfully.")
    }
    else{
        print("Failed to install package.")
    }

    sys.path.append(cwd) // Add the path to your custom package
    let myTexttoAudiolib = Python.import("TexttoAudio")

    app.get { req -> EventLoopFuture<View> in
        return req.view.render("index.html")
    }

    app.post("convert") { req -> EventLoopFuture<String> in
        let upload = try req.content.decode(Config.self)
        pythonQueue.sync {
            let conversation = upload.conversation
            let speakerData = upload.speaker_data
            let jsonResponse = myTexttoAudiolib.main(conversation, speakerData)
            let extractedText = String(describing: jsonResponse)
            // Specify the type explicitly for utf8
            let jsonData = extractedText.data(using: String.Encoding.utf8)
            if let jsonData = jsonData {
                let jsonDict = try? JSONSerialization.jsonObject(with: jsonData) as? [String: Any]
                if let audioBase64 = jsonDict?["text"] as? String {
                    // Use optional binding to safely unwrap audioBase64
                    // Assuming audioData is your Data object containing audio content
                    if let audioData = Data(base64Encoded: audioBase64) {
                        let fileManager = FileManager.default

                        // Specify the file name and extension
                        let fileName = "audioFile"
                        let fileExtension = "mp3" // change this to the appropriate format if different

                        // Get the URL for the document directory
                        do {
                            let currentDirectoryURL = URL(fileURLWithPath: fileManager.currentDirectoryPath)
                            let fileURL = currentDirectoryURL.appendingPathComponent("\(fileName).\(fileExtension)")

                            // Write the data to the file
                            try audioData.write(to: fileURL)

                            print("Audio file saved: \(fileURL)")
                        } catch {
                            print("Error saving file: \(error)")
                        }
                    }
                } else {
                    // Handle the case where audioBase64 is nil
                    print("audioBase64 is null")
                }
            } else {
                // Handle the case where jsonData is nil
                print("jsonData is null")
            }
            print("sync is working correctly")
        }
        return req.eventLoop.future("data sent")
    }

    app.get("list") { req -> Response in
        do {
            let audioFiles = try getListOfAudioFiles() // Assuming you have this function
            var fileListHTML = ""

            for file in audioFiles {
                fileListHTML += "<li>\(file)</li>"
            }

            let resourcesDirectory = app.directory.resourcesDirectory
            let templatePath = resourcesDirectory + "Views/uploadSuccess.html"
            var htmlContent = try String(contentsOfFile: templatePath, encoding: .utf8)

            htmlContent = htmlContent.replacingOccurrences(of: "{{audioList}}", with: fileListHTML)

            // Create a custom response with the correct content type
            var headers = HTTPHeaders()
            headers.add(name: .contentType, value: "text/html")
            return Response(status: .ok, headers: headers, body: Response.Body(string: htmlContent))
        } catch {
            // Handle error
            let response = Response(status: .internalServerError, body: Response.Body(string: "Error: \(error)"))
            return response
        }
    }
}

func getDocumentsDirectory() -> URL {
    FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
}