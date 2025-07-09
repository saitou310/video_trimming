pipeline {
    agent any

    environment {
        P4_CRED_ID = 'your-p4-credential-id'
        P4_STREAM = '//depot/stream/main'
        BASELINE_FILE = 'baseline_cl.txt'
        SLACK_CHANNEL = '#your-channel'
        P4PORT = 'perforce:1666'
        P4USER = 'jenkins'
        // 必要なら P4CLIENT も追加で定義
    }

    triggers {
        pollSCM('H/5 * * * *')
    }

    stages {
        stage('Check for Changes') {
            steps {
                script {
                    def baselineCL = '0'
                    if (fileExists(env.BASELINE_FILE)) {
                        baselineCL = readFile(env.BASELINE_FILE).trim()
                        echo "Previous CL: ${baselineCL}"
                    }

                    // 最新CL取得（p4 CLI）
                    def latestCL = bat(
                        script: "p4 -p ${env.P4PORT} -u ${env.P4USER} changes -m1 ${env.P4_STREAM}",
                        returnStdout: true
                    ).trim()

                    def match = latestCL =~ /Change\s+(\d+)/
                    if (!match) {
                        error "Could not extract latest changelist number"
                    }

                    latestCL = match[0][1]
                    echo "Latest CL: ${latestCL}"

                    if (latestCL.toInteger() > baselineCL.toInteger()) {
                        echo "New changes detected since CL ${baselineCL}"

                        def desc = bat(
                            script: "p4 -p ${env.P4PORT} -u ${env.P4USER} describe -s ${latestCL}",
                            returnStdout: true
                        ).trim()

                        slackSend(
                            channel: env.SLACK_CHANNEL,
                            message: "*New Perforce Submit Detected!*\n" +
                                     "Stream: `${env.P4_STREAM}`\n" +
                                     "Change: `${latestCL}`\n" +
                                     "```" + desc + "```"
                        )

                        writeFile file: env.BASELINE_FILE, text: latestCL
                    } else {
                        echo "No new changelists."
                    }
                }
            }
        }
    }
}
